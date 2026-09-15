# Guide de développement

Pour lancer la stack locale, voir le [README](../README.md) et [local/README.md](../local/README.md). Ce guide couvre le travail sur le code.

## Environnement hors conteneurs

Utile pour l'autocomplétion de l'IDE, les tests et le lint.

### Backend

Le projet utilise [uv](https://docs.astral.sh/uv/), qui installe aussi la bonne version de Python (3.11).

`mysqlclient` se compile à l'installation : il faut d'abord les outils de build, `pkg-config` et les en-têtes MySQL ou MariaDB. Voir [le guide de mysqlclient](https://github.com/PyMySQL/mysqlclient#install) pour votre système.

```sh
cd backend
uv sync                      # crée .venv/ avec les dépendances de dev
uv add <paquet>              # ajoute une dépendance
uv add --group dev <paquet>  # ajoute une dépendance de dev uniquement
```

### Frontend

```sh
cd frontend
yarn install --frozen-lockfile
yarn add <paquet>
```

## Ajouter une fonctionnalité

Exemple d'une nouvelle route dans un module existant.

1. **Spec** : décrire la route et ses modèles dans `openapi/spec.yaml`.
2. **Génération** : `make generate` régénère les entités du backend et le client du frontend.
3. **Base de données**, si besoin : modifier le modèle dans `<module>/storage/models.py` et écrire la migration (voir plus bas).
4. **Interface** : ajouter la méthode dans `<module>/interfaces/`.
5. **Repository** : l'implémenter dans `<module>/storage/`, en restant sur des opérations simples.
6. **Manager** : écrire la logique métier dans `<module>/<module>_manager.py`, sans importer ni FastAPI ni SQLAlchemy.
7. **Route** : l'ajouter dans `<module>/router.py`, vérifier les droits avec `require_role_or_ownership` et traduire les exceptions métier en codes HTTP. Le manager est construit par une fonction `get_<module>_manager`, injectée avec `Depends`.
8. **Tests** : un test unitaire du manager avec des repositories simulés, et un test d'intégration de la route.
9. **Frontend** : utiliser le service généré (`frontend/src/app/api/`) dans un composant, déclarer la route dans `app-routing.module.ts` si c'est une nouvelle page, puis `yarn i18n:extract` : les nouvelles entrées sont ajoutées sans `<target>` dans `messages.en.xlf`, il suffit de les compléter.

Pour un **nouveau module**, reprendre la structure d'un module existant (`room/` est l'un des plus simples) et enregistrer son router dans `backend/adh6/main.py` avec `app.include_router(..., prefix="/api")`.

## Migrations

Les migrations sont dans `backend/migrations/versions/` et s'appliquent au démarrage du backend.

```sh
cd backend
uv run alembic revision -m "description"   # crée une migration vide à compléter
uv run alembic upgrade head
```

**Attention à `--autogenerate`** : `migrations/env.py` ne charge que les anciens modèles communs (6 tables), pas ceux des modules. Une migration autogénérée proposerait de supprimer la plupart des tables. Écrivez la migration à la main, ou relisez chaque ligne du fichier généré.

Une migration doit fonctionner à la fois sur **MySQL** (local) et sur **MariaDB** (production). Par exemple, `DROP INDEX IF EXISTS` n'existe pas en MySQL : vérifiez l'existence de l'index avec `sa.inspect()`.

## Tests et qualité

| Commande | Effet |
|---|---|
| `make test-backend` | Tous les tests backend |
| `uv run pytest test/unit/...` | Un fichier ou un dossier précis (dans `backend/`) |
| `make check-backend` | `ruff format`, `ruff check --fix`, `pyright`, puis les tests |
| `yarn lint` | Lint du frontend |
| `yarn prettier` | Corrige le formatage du frontend |
| `yarn prettier:check` | Vérifie le formatage sans rien modifier |

- **Tests unitaires** (`backend/test/unit/`) : un manager isolé, avec des repositories simulés.
- **Tests d'intégration** (`backend/test/integration/`) : l'application complète via `TestClient`, sur une base SQLite. Les tokens Keycloak y sont remplacés par des faux tokens et Elasticsearch est désactivé.
- La CI ne contrôle que le backend (`tox -e ci`) : elle échoue si la couverture passe sous 75 %, si le formatage n'est pas respecté ou si pyright trouve une erreur. Le lint et le formatage du frontend ne sont pas vérifiés en CI : lancez-les avant de pousser.

## Génération de code

`spec-to-code.sh` (appelé par `make generate`) lance openapi-generator dans Docker et écrase :

- `backend/adh6/entity/`
- `frontend/src/app/api/`

Ces dossiers ne se modifient jamais à la main : toute modification serait perdue à la prochaine génération. La version du générateur est épinglée à v7.11.0, car les versions suivantes ont [un bug](https://github.com/OpenAPITools/openapi-generator/issues/21182) qui casse la génération.

## Où modifier quoi

| Besoin | Où |
|---|---|
| Contrat d'API | `openapi/spec.yaml` |
| Logique métier | `backend/adh6/<module>/*_manager.py` |
| Route HTTP, droits d'accès | `backend/adh6/<module>/router.py` |
| Accès à la base | `backend/adh6/<module>/storage/` |
| Schéma de la base | `backend/adh6/<module>/storage/models.py` et `backend/migrations/versions/` |
| Pilotage des switches | `backend/adh6/network/snmp/` |
| Mails et leurs templates | `backend/adh6/mail/` |
| Paramètres du backend | `backend/adh6/config/configuration.py` (lus depuis les variables d'environnement) |
| Pages et composants | `frontend/src/app/<fonctionnalité>/` |
| Routes du frontend | `frontend/src/app/app-routing.module.ts` |
| Config frontend par environnement | `frontend/src/environments/` |
| Traductions | `frontend/src/local/messages.en.xlf` |
| Styles globaux | `frontend/src/styles.scss` |
| Stack locale | `compose.yaml`, `local/` |

## Dossiers transverses du backend

| Dossier | Rôle |
|---|---|
| `default/` | Bases réutilisables : `CRUDManager`, `CRUDRepository`, et `DefaultHandler` pour les anciens handlers |
| `storage/` | Base SQLAlchemy commune (`Base`), `count_rows` pour les compteurs de pagination, anciens modèles partagés, et une façade synchrone gardée pour d'anciens tests |
| `decorator/` | `log_call` et `with_context` |
| `misc/` | Profil de l'utilisateur connecté, validateurs (MAC…) |
| `utils/` | Filtres et validateurs partagés |
| `*/http/` | Anciens handlers de l'époque Connexion, que les routes FastAPI n'utilisent plus |
