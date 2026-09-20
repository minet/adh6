# Architecture

## Backend

Le code est dans `backend/adh6/`, découpé en modules. Chaque module suit une architecture en couches inspirée de la [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) : la logique métier ne dépend ni de FastAPI ni de SQLAlchemy, ce qui la rend testable et remplaçable.

### Couches d'un module

Exemple avec `device/` :

| Fichier | Rôle |
|---|---|
| `router.py` | Routes FastAPI : lit la requête, vérifie les droits |
| `device_manager.py` | Logique métier (validation de la MAC, limites, attribution d'IP) |
| `interfaces/` | Interfaces abstraites des dépendances du manager (`DeviceRepository`, `LogsRepository`…) |
| `storage/` | Implémentations : modèles SQLAlchemy (`models.py`) et repositories |

Les entités échangées entre couches (`backend/adh6/entity/`) sont des modèles Pydantic générés depuis la spec OpenAPI.

La règle : un manager ne connaît que des interfaces et des entités, jamais un repository concret ni un objet FastAPI. Les dépendances sont injectées dans `router.py` via `Depends`.

### Exemple : créer un appareil

1. `POST /api/device` arrive dans `device/router.py`, qui vérifie le rôle `network:write` ou que l'appareil est pour soi.
2. `DeviceManager.create` vérifie la MAC, l'adhérent et sa chambre, les doublons et la limite de 20 appareils, puis appelle `DeviceRepository.create`.
3. `DeviceSQLRepository` (`device/storage/`) écrit en base avec SQLAlchemy.
4. Le manager attribue ensuite une IP dans le VLAN de la chambre, via `DeviceIpManager`.
5. Les exceptions métier (`DeviceAlreadyExists`, `MemberNotFoundError`…) remontent au router, qui les traduit en 400 ou 404.

### Modules

| Module | Rôle |
|---|---|
| `authentication` | OIDC, API keys, correspondance rôles ↔ utilisateurs |
| `member` | Adhérents, cotisations ([cycle de vie](adhesions.md)), charte, mailing lists |
| `device` | Appareils, attribution d'IP, logs de connexion |
| `room` | Chambres et leurs occupants |
| `network` | Switches et ports, pilotés en SNMP |
| `subnet` | VLANs et plages d'adresses |
| `treasury` | Transactions, produits, moyens de paiement, exports |
| `naina` | Rôles temporaires |
| `mail` | SMTP, templates de mails |
| `metrics` | Santé de l'API |
| `misc` | Profil de l'utilisateur connecté, validateurs |

Shared : `config/`, `security.py`, `database.py`, `exceptions.py`.

### Base de données

- SQLAlchemy en async (`aiomysql`). Les modèles sont dans les `storage/models.py` de chaque module.
- Les migrations Alembic sont dans `backend/migrations/versions/` et s'appliquent au démarrage du conteneur (`alembic upgrade head`).
- Nouvelle migration : `uv run alembic revision --autogenerate -m "description"` dans `backend/`.
- Les tests utilisent SQLite, sans base externe.

## Authentification et droits

- Le backend mène lui-même la connexion OIDC (code d'autorisation + PKCE) : le navigateur ne voit jamais de token. Les routes sont dans `authentication/session/` sous `/api/auth/` (`login`, `callback`, `refresh`, `logout`), hors de la spec OpenAPI.
  - `GET /api/auth/login?return_to=/fr/page` mémorise la tentative dans un cookie signé `adh6_oidc_login` (état, nonce, vérificateur PKCE, page de retour ; 10 minutes ; `SameSite=Lax`) puis redirige vers Keycloak. Le callback exige ce cookie : il lie la connexion au navigateur qui l'a lancée.
  - Une fois connecté, la session tient dans les cookies `adh6_access`, `adh6_refresh` et `adh6_id` : `HttpOnly`, `Secure`, `SameSite=Strict`, `Path=/api`. Le frontend renouvelle l'accès avec `POST /api/auth/refresh` quand l'API répond 401, et se déconnecte avec `POST /api/auth/logout`.
  - Les requêtes qui modifient des données, authentifiées par cookie, doivent porter l'en-tête `X-Requested-With: XMLHttpRequest` et ne pas venir d'un autre site (`Sec-Fetch-Site`, `Origin`). Les appels par `Authorization: Bearer` ou `X-API-KEY` ne sont pas concernés : le navigateur ne les ajoute pas tout seul.
  - Réglages : `SESSION_SECRET` (obligatoire), `ADH6_URL` ou `OIDC_REDIRECT_URI` (URL du callback), `SESSION_COOKIE_SECURE`, `OIDC_SCOPE`, `OIDC_CLIENT_SECRET` (seulement si le client Keycloak devient confidentiel).
- Le backend vérifie chaque token d'accès (cookie, ou `Bearer` pour les autres clients) localement, avec les clés publiques du realm MiNET de Keycloak. Il lit `preferred_username` et `groups`. Sans identité, l'API répond 401 (403 si l'utilisateur est connecté mais n'a pas le droit).
- Les rôles viennent de la table `role_mappings` : soit par login (`authentication = USER`), soit par groupe Keycloak (`authentication = OIDC`). Les clés d'API ont leurs propres rôles.
- Rôles : `user`, `admin:read`, `admin:write`, `admin:prod`, `treasurer:read`, `treasurer:write`, `network:read`, `network:write`, `network:write:prod`, `network:write:dev`, `network:write:hosting`.
- Dans les routes, `require_role_or_ownership` autorise l'accès si l'utilisateur a le rôle demandé ou possède la ressource.

## Switches (SNMP)

`network/snmp/switch_network_manager.py` pilote les switches Cisco avec `pysnmp`. Un port est identifié par son OID, qui est l'`ifIndex` de l'interface sur le switch.

| Fonction | MIB |
|---|---|
| État du port, vitesse, alias, découverte des ports | `IF-MIB` |
| VLAN du port, voice VLAN | `CISCO-VLAN-MEMBERSHIP-MIB` |
| MAC Authentication Bypass | `CISCO-MAC-AUTH-BYPASS-MIB` |
| 802.1X | `IEEE8021-PAE-MIB` |
| Preset Mini-Routeur | `CISCO-AUTH-FRAMEWORK-MIB` |

La communauté SNMP de chaque switch est en base. Passer un port sur certains VLANs sensibles demande le rôle `admin:write`. En local, le service `snmpsim` simule un switch.

## Logs de connexion

Les logs RADIUS et DHCP d'un adhérent sont lus dans Elasticsearch (`device/storage/logs_repository.py`) si `ELK_ENABLED` est actif. Sinon, la liste est vide et le reste de l'application fonctionne normalement.

## Frontend

- Angular 20, composants dans `frontend/src/app/`, un dossier par fonctionnalité (`member/`, `device/`, `room/`, `switch/`, `port/`, `transaction/`…).
- Le client de l'API (`frontend/src/app/api/`) est généré depuis la spec : il ne se modifie pas à la main.
- Configuration par environnement dans `frontend/src/environments/` (`environment.ts` en local, `environment.prod.ts` en production).
- Langue source : français. Traduction anglaise dans `frontend/src/local/messages.en.xlf`, extraction avec `yarn i18n:extract` (`ng-extract-i18n-merge` fusionne les nouvelles entrées dans le fichier anglais).

## Génération de code

`openapi/spec.yaml` est la source de vérité du contrat d'API. `spec-to-code.sh` (appelé par `make generate`) utilise openapi-generator dans Docker pour produire :

- les entités Pydantic du backend (`backend/adh6/entity/`) ;
- le client TypeScript du frontend (`frontend/src/app/api/`).

Les routes du backend s'écrivent à la main. `backend/test/integration/test_openapi_contract.py` vérifie qu'elles restent cohérentes avec la spec.
