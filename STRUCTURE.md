# Structure du projet ADH6

## Vue d'ensemble

ADH6 est le système de gestion d'adhérents de l'association MiNET. Il s'agit d'une application web complète avec une architecture moderne séparant le frontend du backend.

L'application permet de :

- Gérer les adhésions et les cotisations
- Gérer les appareils des membres (attribution d'adresses IP)
- Gérer les chambres et leurs attributions
- Gérer le réseau (switches, ports, VLANs)
- Assurer le suivi de la trésorerie

### Architecture globale

Le projet est structuré selon une architecture client-serveur moderne :

- **Backend** : API REST développée en Python avec Flask/Connexion, suivant les principes de la Clean Architecture
- **Frontend** : Application Angular (version 15)
- **API** : Spécification OpenAPI (anciennement Swagger) pour la communication entre frontend et backend
- **Base de données** : MySQL/MariaDB
- **Infrastructure** : Conteneurs Docker pour le développement et le déploiement

### Répertoire racine

Les fichiers principaux à la racine sont :

- `docker-compose.yml` : Configuration des services Docker pour le développement local
- `docker-compose-deploy.yml` : Configuration des services Docker pour le déploiement
- `openapi/spec.yaml` : Spécification de l'API
- `Makefile` : Commandes pour faciliter le développement
- `README.md` : Documentation principale du projet
- `requirements.txt` : Dépendances Python globales

### Technologies utilisées

- **Backend** : Python, Flask, Connexion, SQLAlchemy
- **Frontend** : Angular, TypeScript, Bulma CSS
- **API** : OpenAPI/Swagger
- **Base de données** : MySQL/MariaDB
- **Authentification** : OAuth2, CAS
- **Déploiement** : Docker, Docker Compose

## Organisation des dossiers

Le projet est organisé en plusieurs dossiers principaux :

- `/api_server/` : Code source du backend Python
- `/frontend_angular/` : Code source du frontend Angular
- `/openapi/` : Spécification de l'API
- `/reverse_proxy/` : Configuration du reverse proxy (NGINX)
- `/doc/` : Documentation supplémentaire

Chacun de ces dossiers est détaillé dans les sections suivantes.

## Backend (`/api_server/`)

Le backend suit une architecture "Clean Architecture" (ou "Onion Architecture") telle que définie par Robert C. Martin (Uncle Bob). Cette approche permet de séparer les préoccupations et de rendre le code plus maintenable.

### Structure du backend

- `/api_server/adh6/` : Code source principal du backend
- `/api_server/migrations/` : Scripts de migration de la base de données
- `/api_server/test/` : Tests unitaires et d'intégration
- `/api_server/openapi/` : Fichiers de configuration OpenAPI

### Architecture modulaire

Le backend est organisé en modules fonctionnels, chacun gérant une partie distincte de l'application. Chaque module suit la même structure en couches :

#### Couches de la Clean Architecture

1. **Entity Layer (Layer 1)** - Entités
   - Structures de données qui représentent les concepts métier
   - Se trouvent dans le dossier global du backend plutôt que dans les modules

2. **Use Case Layer (Layer 2)** - Cas d'utilisation
   - Contient la logique métier (business logic)
   - Implémentée dans les "managers" à la racine de chaque module (ex: `member_manager.py`)
   - Indépendante des technologies et frameworks spécifiques

3. **Interface Handler Layer (Layer 3)** - Gestionnaires d'interface
   - Adapte les entrées/sorties pour le Use Case Layer
   - Comprend les handlers HTTP et les repositories de stockage
   - Se trouve dans les sous-dossiers `http` et `storage` de chaque module

4. **Framework & Drivers Layer (Layer 4)** - Frameworks et drivers
   - Bibliothèques et frameworks externes (Flask, SQLAlchemy, etc.)
   - Définis dans les requirements.txt

### Modules principaux

- **authentication** : Gestion de la sécurité des endpoints et des informations d'authentification (clés API, rôles utilisateur)
- **member** : Gestion des utilisateurs et de leurs cotisations
- **device** : Gestion des appareils des membres et attribution des adresses IP
- **room** : Gestion des chambres
- **network** : Gestion des appareils réseau
- **subnet** : Gestion des sous-réseaux à attribuer
- **treasury** : Gestion de la trésorerie
- **metrics** : Gestion des métriques de la plateforme

### Structure interne d'un module

Prenons l'exemple du module `device` :

```
/api_server/adh6/device/
  __init__.py
  device_manager.py             # Layer 2: Use Case (logique métier)
  /http
    device.py                   # Layer 3: Interface pour l'API HTTP
  /interfaces
    device_repository.py        # Layer 3: Interface abstraite pour le stockage
  /storage
    device_repository.py        # Layer 3: Implémentation de l'interface (SQL)
```

### Flux de travail typique dans le backend

1. Une requête HTTP arrive et est interceptée par Connexion/Flask
2. Elle est dirigée vers le handler HTTP approprié (Layer 3)
3. Le handler appelle le manager correspondant (Layer 2)
4. Le manager implémente la logique métier et utilise les repositories (Layer 3) pour accéder aux données
5. Les repositories interagissent avec la base de données via SQLAlchemy (Layer 4)
6. La réponse remonte cette chaîne et est renvoyée au client

### Base de données et migrations

Les migrations de la base de données sont gérées par Alembic (via Flask-Migrate) et sont stockées dans le dossier `/api_server/migrations/`.

### Communication avec la base de données

ADH6 utilise une architecture de base de données robuste basée sur SQLAlchemy, un ORM (Object-Relational Mapping) Python qui facilite l'interaction avec la base de données MySQL/MariaDB.

#### Configuration de la base de données

La configuration de la base de données est centralisée dans `/api_server/adh6/config/configuration.py` et varie selon l'environnement :

1. **Développement local** :
   - En développement, une base de données MySQL est lancée dans un conteneur Docker
   - Les paramètres sont configurés dans le fichier `.env` à la racine du projet

2. **Production** :
   - En production, l'application se connecte à une base de données externe
   - Les paramètres de connexion sont injectés via des variables d'environnement :

   ```python
   SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://{}:{}@{}/{}".format(
       os.environ.get("DATABASE_USERNAME"),
       os.environ.get("DATABASE_PASSWORD"),
       os.environ.get("DATABASE_HOST"),
       os.environ.get("DATABASE_DB_NAME")
   )
   ```

3. **Tests** :
   - Pour les tests, une base de données SQLite en mémoire est utilisée
   - Cela permet d'exécuter les tests rapidement sans dépendance externe

#### Architecture d'accès aux données

L'accès aux données suit le principe de la Clean Architecture :

1. **Modèles SQLAlchemy** :
   - Définis dans les dossiers `storage/models.py` de chaque module
   - Exemple : `/api_server/adh6/network/storage/models.py` pour les modèles réseau

2. **Repositories** :
   - Implémentent les interfaces abstraites de chaque module
   - Traduisent les opérations CRUD en requêtes SQLAlchemy
   - Exemple : `DeviceSQLRepository` dans `/api_server/adh6/device/storage/device_repository.py`

3. **Session SQLAlchemy** :
   - Gérée par Flask-SQLAlchemy
   - Instance globale disponible via `adh6.storage.db.session`

#### Migrations de base de données

Les migrations sont gérées par Alembic (via Flask-Migrate) :

- Les scripts de migration sont stockés dans `/api_server/migrations/versions/`
- Ils permettent de faire évoluer le schéma de la base de données tout en préservant les données
- Les migrations sont exécutées automatiquement lors du déploiement

Exemple de migration :

```python
def upgrade():
    op.alter_column('ports', 'numero',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
```

#### Fonctionnalités avancées

1. **Tracking des modifications** :
   - Utilisation de classes comme `RubyHashTrackable` pour suivre les modifications
   - Les changements sont enregistrés dans la table `modifications`

2. **Connection pooling** :
   - Configuration du pool de connexions via `SQLALCHEMY_ENGINE_OPTIONS`
   - Détection des connexions inactives avec `pool_pre_ping=True`

3. **Isolation des transactions** :
   - Niveau d'isolation configurable via `isolation_level`
   - Par défaut réglé sur `SERIALIZABLE` pour garantir la cohérence

#### Sécurité

La sécurité de la base de données est assurée par plusieurs mécanismes :

1. **Credentials sécurisés** :
   - Les identifiants ne sont jamais en dur dans le code
   - En production, ils sont injectés via des variables d'environnement
   - En développement, ils sont définis dans le fichier `.env` (non versionné)

2. **ORM** :
   - L'utilisation de SQLAlchemy limite les risques d'injection SQL
   - Les paramètres sont liés de manière sécurisée

3. **Isolation** :
   - En production, la base de données est accessible uniquement depuis l'application
   - Des règles de pare-feu limitent les accès externes

#### Monitoring et logs

En production, l'application peut être configurée pour envoyer les logs et métriques à un système ELK (Elasticsearch, Logstash, Kibana) :

```python
if os.environ.get("ELK_ENABLED", False):
    # Configuration des hôtes Elasticsearch
    ELK_HOSTS = [
        {
            'scheme': s.group('scheme'), 
            'host': s.group('host'), 
            'port': int(s.group('port'))
        }
        # ...
    ]
```

Cela permet de surveiller les performances de la base de données et de détecter les problèmes potentiels.

### Système de logs et monitoring

ADH6 dispose d'un système de logs robuste qui permet le suivi des activités des utilisateurs et le debugging des problèmes de connexion. Ce système est particulièrement utile pour les administrateurs qui aident les membres à résoudre leurs problèmes de réseau.

#### Architecture du système de logs

Le système de logs suit également l'architecture en couches de la Clean Architecture :

1. **Interface abstraite** :
   - Définie dans `/api_server/adh6/device/interfaces/logs_repository.py`
   - La classe `LogsRepository` définit l'interface abstraite avec la méthode `get`

2. **Implémentation concrète** :
   - Implémentée dans `/api_server/adh6/device/storage/logs_repository.py`
   - La classe `ElasticsearchLogsRepository` fournit l'accès aux logs stockés dans Elasticsearch

3. **Manager intermédiaire** :
   - Défini dans `/api_server/adh6/device/device_logs_manager.py`
   - La classe `DeviceLogsManager` coordonne la récupération des appareils d'un membre et leurs logs associés

4. **Accès depuis la couche métier** :
   - Implémenté dans `/api_server/adh6/member/member_manager.py`
   - La méthode `get_logs` du `MemberManager` permet de récupérer les logs formatés pour un membre spécifique

#### Stockage des logs

Les logs sont principalement stockés dans Elasticsearch, ce qui permet :

1. **Recherche rapide** : Elasticsearch est optimisé pour les requêtes textuelles complexes
2. **Stockage à grande échelle** : Capable de gérer des volumes importants de logs
3. **Agrégation et visualisation** : Compatible avec Kibana pour créer des tableaux de bord

#### Types de logs disponibles

ADH6 gère deux types principaux de logs :

1. **Logs d'authentification** (RADIUS) :
   - Traces des tentatives de connexion au réseau
   - Informations sur le statut de l'authentification (succès/échec)
   - Association entre adresses MAC et utilisateurs

2. **Logs DHCP** (optionnels) :
   - Traces des allocations d'adresses IP
   - Informations sur les baux DHCP
   - Ces logs peuvent être activés à la demande via le paramètre `dhcp=True`

#### Requêtes Elasticsearch

Les requêtes Elasticsearch sont construites dynamiquement en fonction des besoins :

1. **Filtrage par utilisateur** : Récupération des logs mentionnant un nom d'utilisateur spécifique
2. **Filtrage par appareil** : Recherche des logs concernant des adresses MAC particulières
3. **Variations d'adresses MAC** : Prise en compte de différents formats d'adresses MAC pour améliorer les résultats

Exemple de construction de requête :

```python
query = {
    "sort": {
        '@timestamp': 'desc',  # Tri chronologique inverse
    },
    "query": {
        "bool": {
            "filter": {
                "match": {"program": "radiusd"}  # Filtre les logs RADIUS
            },
            "should": [
                # Recherche par nom d'utilisateur
                {"match": {"radius_user": member.username}},
                # Les adresses MAC sont ajoutées dynamiquement
            ],
            "minimum_should_match": 1,
        },
    },
    "_source": ["@timestamp", "message", "program", "src_mac"],  # Champs à récupérer
    "size": limit,  # Limitation du nombre de résultats
}
```

#### Accès aux logs depuis le frontend

Le frontend permet aux administrateurs et aux utilisateurs de visualiser les logs pertinents :

1. **Pour les administrateurs** : Vue complète des logs d'un membre via la page de détails du membre
2. **Pour les utilisateurs** : Accès limité à leurs propres logs via leur tableau de bord

L'interface utilisateur propose des options pour :

- Filtrer les types de logs (avec/sans DHCP)
- Actualiser les logs à la demande
- Afficher les logs dans un format lisible avec mise en forme

#### Fallback en cas d'indisponibilité

Le système est conçu pour fonctionner même si Elasticsearch n'est pas disponible :

```python
try:
    logs = self.device_logs_manager.get(member=member, dhcp=dhcp)
    # Traitement des logs
except LogFetchError:
    logging.warning("log_fetch_failed")
    return []  # Mode dégradé : retourne une liste vide
```

#### Configuration du système de logs

La configuration du système ELK (Elasticsearch, Logstash, Kibana) est définie dans `/api_server/adh6/config/configuration.py` :

```python
if os.environ.get("ELK_ENABLED", False):
    # Configuration des hôtes Elasticsearch
    ELK_HOSTS = [
        {
            'scheme': s.group('scheme'),
            'host': s.group('host'),
            'port': int(s.group('port'))
        }
        # ...
    ]
```

En environnement de développement, un système de logs simplifié est utilisé pour faciliter les tests.

### Tests

Les tests se trouvent dans le dossier `/api_server/test/` et sont séparés en tests unitaires (`/unit/`) et tests d'intégration (`/integration/`).

## Frontend (`/frontend_angular/`)

Le frontend est une application Angular moderne qui communique avec le backend via l'API REST.

### Structure du frontend

- `/frontend_angular/src/app/` : Modules, composants et services Angular
- `/frontend_angular/src/assets/` : Ressources statiques (images, icônes, fichiers de traduction)
- `/frontend_angular/src/environments/` : Configurations pour les différents environnements
- `/frontend_angular/nginx/` : Configuration NGINX pour le déploiement

### Architecture du frontend

Le frontend est structuré par modules fonctionnels, chacun représentant une partie de l'application :

- **Module principal** (`app.module.ts`) : Module racine de l'application
- **Module de routage** (`app-routing.module.ts`) : Définit les routes de l'application

### Composants principaux

Chaque fonctionnalité est implémentée à travers un ensemble de composants Angular spécifiques :

- **Composants de membre** (`/member/`) : Gestion des profils d'adhérents
  - Liste des membres (`list.component.ts` dans `/member/list/`)
  - Vue détaillée d'un membre (`view.component.ts`)
  - Édition d'un membre (`create-or-edit.component.ts`)

- **Composants d'appareil** (`/device/`, `/member-device/`) : Gestion des appareils
  - Liste des appareils (`list/list.component.ts`)
  - Détails d'un appareil (`list/element/element.component.ts`)

- **Composants de chambre** (`/room/`) : Gestion des chambres
  - Liste des chambres (`room-list.component.ts`)
  - Détails d'une chambre (`room-details.component.ts`)

- **Composants réseau** (`/switch/`, `/port/`) : Gestion des équipements réseau
  - Liste des switches (`switch-list.component.ts`)
  - Détails d'un switch (`switch-details.component.ts`)
  - Liste des ports (`port-list.component.ts`)
  - Détails d'un port (`port-details.component.ts`)

- **Composants de trésorerie** (`/treasury/`, `/transaction/`, `/account/`) : Gestion financière
  - Vue trésorerie (`treasury.component.ts`)
  - Liste des transactions (`transaction-list.component.ts`)
  - Liste des comptes (`account-list.component.ts`)

- **Composants d'authentification** (`/auth-management/`) : Gestion des accès
  - Gestion des clés API (`api-key.component.ts`)

- **Interface utilisateur** : Composants génériques pour l'UI
  - Barre de navigation (`navbar.component.ts`)
  - Barre de navigation verticale (`vertical-navbar.component.ts`)
  - Pied de page (`footer.component.ts`)
  - Pagination (`pagination.component.ts`)

### Services et modèles

Les services Angular sont générés automatiquement à partir de la spécification OpenAPI :

- `/frontend_angular/src/app/api/` : Services pour communiquer avec l'API
- `/frontend_angular/src/app/api/model/` : Modèles de données générés

### Interface utilisateur

L'interface utilisateur est construite avec le framework CSS Bulma, qui fournit des composants responsives et modernes. Les icônes sont gérées avec Font Awesome.

### Internationalisation

Le frontend supporte l'internationalisation avec des fichiers de traduction pour différentes langues :

- `/frontend_angular/src/local/` : Fichiers de traduction

### Routing

Le système de routage d'Angular est utilisé pour naviguer entre les différentes vues :

- La page d'accueil (`/portail`) pour les utilisateurs non authentifiés
- Le tableau de bord (`/dashboard`) pour les utilisateurs connectés
- Les différentes sections pour la gestion des membres, appareils, etc.

### Authentification

L'authentification utilise le protocole OAuth2 via le service CAS (Central Authentication Service) de MiNET. L'application utilise la bibliothèque `angular-auth-oidc-client` pour gérer l'authentification côté client.

## API (`/openapi/`)

L'API est au cœur de la communication entre le frontend et le backend. Elle est définie selon la spécification OpenAPI (anciennement Swagger).

### Fichier de spécification

- `/openapi/spec.yaml` : Définit toutes les routes, modèles et opérations disponibles dans l'API

Cette spécification est utilisée pour :

1. Générer le code du côté serveur (Python/Flask) via la bibliothèque Connexion
2. Générer le code client (TypeScript) pour le frontend Angular
3. Générer la documentation interactive de l'API

### Génération de code

La génération du code est automatisée via des commandes dans le Makefile :

- Pour le backend : génère les interfaces Python avec OpenAPI Generator
- Pour le frontend : génère les services et modèles TypeScript

### Principales routes de l'API

Les principales routes de l'API sont organisées par ressource :

- `/health` : Vérification de l'état de l'API
- `/profile` : Informations sur l'utilisateur connecté
- `/member/` : Gestion des membres
- `/device/` : Gestion des appareils
- `/room/` : Gestion des chambres
- `/switch/` : Gestion des switches réseau
- `/port/` : Gestion des ports des switches
- `/vlan/` : Gestion des VLANs
- `/account/` : Gestion des comptes pour la trésorerie
- `/transaction/` : Gestion des transactions financières

### Authentification de l'API

L'API utilise deux méthodes d'authentification :

- OAuth2 pour les utilisateurs via l'interface web
- Clés API pour les accès programmatiques et les services automatisés (accessible une fois qu'on a la prod)

## Communication avec les systèmes externes

### Communication avec les switches réseau

ADH6 communique directement avec les équipements réseau (switches) à l'aide du protocole SNMP (Simple Network Management Protocol). Cette fonctionnalité est implémentée dans le module `network/snmp`.

#### Architecture de la communication SNMP

La communication avec les switches suit le même principe d'architecture en couches que le reste de l'application :

1. **Interface abstraite** : Définie dans `/api_server/adh6/network/interfaces/switch_network_manager.py`
2. **Implémentation SNMP** : Implémentée dans `/api_server/adh6/network/snmp/switch_network_manager.py`

La classe principale `SwitchSNMPNetworkManager` implémente l'interface `SwitchNetworkManager` et fournit les méthodes pour interagir avec les switches via SNMP.

#### Fonctionnalités SNMP principales

- **Gestion des ports** : Activation/désactivation des ports (`update_port_status`)
- **Gestion des VLANs** : Lecture et attribution de VLANs aux ports (`get_port_vlan`, `update_port_vlan`)
- **Gestion de l'authentification** : Configuration de l'authentification par port (`get_port_auth`, `update_port_auth`)
- **MAC Authentication Bypass (MAB)** : Activation/désactivation du MAB sur les ports (`get_port_mab`, `update_port_mab`)
- **Surveillance des ports** : Récupération de l'état, de la vitesse et de l'alias d'un port (`get_port_status`, `get_port_speed`, `get_port_alias`)

#### Implémentation technique

La communication SNMP est réalisée à l'aide de la bibliothèque Python `pysnmp`. Deux fonctions principales sont utilisées :

- `get_SNMP_value` : Récupère des valeurs depuis le switch
- `set_SNMP_value` : Configure des paramètres sur le switch

Ces fonctions sont définies dans `/api_server/adh6/network/snmp/util/snmp_helper.py`.

#### Sécurité

L'accès aux commandes SNMP est sécurisé via :

- Gestion des communautés SNMP stockées dans la base de données
- Vérification des rôles utilisateur avant d'autoriser les modifications sensibles
- Validation des paramètres pour prévenir les erreurs de configuration

Par exemple, les modifications de VLANs nécessitent des permissions spécifiques selon le VLAN cible :

```python
if (
    Roles.NETWORK_WRITE.value not in roles and
    (
        ((vlan == 3 or vlan == 103) and Roles.NETWORK_DEV.value not in roles)
        or ((vlan == 2 or vlan == 102) and Roles.NETWORK_PROD.value not in roles)
        or ((vlan == 104) and Roles.NETWORK_HOSTING.value not in roles)
    )
):
    raise UnauthorizedError()
```

#### MIBs utilisés

L'application utilise plusieurs MIBs (Management Information Base) standards pour interagir avec les switches :

- `CISCO-VLAN-MEMBERSHIP-MIB` : Gestion des VLANs
- `IF-MIB` : Gestion des interfaces
- `CISCO-MAC-AUTH-BYPASS-MIB` : Configuration du MAC Authentication Bypass
- `IEEE8021-PAE-MIB` : Gestion de l'authentification 802.1X

## Infrastructure et déploiement

### Docker et Docker Compose

Le projet utilise Docker et Docker Compose pour faciliter le développement et le déploiement :

- `/docker-compose.yml` : Configuration pour le développement local
- `/docker-compose-deploy.yml` : Configuration pour le déploiement en production
- `/api_server/Dockerfile` : Image Docker pour le backend
- `/frontend_angular/Dockerfile` : Image Docker pour le frontend
- `/reverse_proxy/Dockerfile` : Image Docker pour le reverse proxy

### Reverse Proxy (`/reverse_proxy/`)

Le reverse proxy (NGINX) est configuré pour :

- Servir l'application frontend
- Rediriger les requêtes API vers le backend
- Gérer les certificats SSL
- Configurer des en-têtes de sécurité appropriés

La configuration se trouve dans `/reverse_proxy/default.conf.template`.

### Environnements

Le projet est configuré pour fonctionner dans plusieurs environnements :

- **Développement** : Configuration locale pour les développeurs
- **Testing** : Environnement de test automatisé
- **Production** : Environnement de production

Les configurations spécifiques à chaque environnement sont définies dans :

- `/api_server/adh6/config/configuration.py` pour le backend
- `/frontend_angular/src/environments/` pour le frontend

## Cas d'utilisation

Les cas d'utilisation sont classés par priorité selon leur importance pour l'application.

### Cas d'utilisation principaux (Core)

Ces fonctionnalités sont critiques et doivent toujours fonctionner :

1. **Gestion des adhésions**
   - Remarque: La méthode `new_membership`  dont il est question dans [README.md] n'existe pas dans l'implémentation actuelle
   - Ajouter un membre (`MemberManager.update_or_create`)
   - Lire le profil d'un membre (`MemberManager.get_by_login`)

2. **Gestion des appareils**
   - Ajouter un appareil (`DeviceManager.update_or_create`)
   - Chercher des appareils (`DeviceManager.search`)

### Cas d'utilisation secondaires (Level 2)

Ces fonctionnalités sont importantes mais moins critiques :

1. **Gestion des profils**
   - Lire les logs d'un membre (`MemberManager.get_logs`)
   - Changer le mot de passe d'un membre (`MemberManager.change_password`)
   - Mettre à jour le profil d'un membre (`MemberManager.update_partially`)
   - Chercher les membres (`MemberManager.search`)

2. **Gestion avancée des appareils**
   - Voir les infos d'un appareil (Remarque: cette fonctionnalité est implémentée via `device_repository.get_by_mac()`)
   - Supprimer un appareil (`DeviceManager.delete`)

### Cas d'utilisation tertiaires (Level 3)

Ces fonctionnalités sont utiles mais non critiques pour l'opération quotidienne :

1. **Gestion administrative**
   - Supprimer un membre (`MemberManager.delete`)

## Guide pour les développeurs

### Comment ajouter une fonctionnalité

Pour ajouter une nouvelle fonctionnalité à ADH6, suivez ces étapes :

1. **Modifier l'API** : Mettez à jour `/openapi/spec.yaml` pour ajouter les nouveaux endpoints ou modèles
2. **Générer le code** : Utilisez `make generate` pour régénérer le code client et serveur
3. **Backend** :
   - Créez/modifiez un manager dans le module approprié (Layer 2)
   - Implémentez la logique métier
   - Créez/modifiez les interfaces de repository si nécessaire
   - Implémentez le repository pour la persistance des données
   - Écrivez des tests
4. **Frontend** :
   - Créez/modifiez les composants Angular nécessaires
   - Utilisez les services générés pour communiquer avec l'API

### Où aller pour modifier

#### Base de données

- Schéma : `/api_server/adh6/entity/`
- Migrations : `/api_server/migrations/`
- Requêtes : Modules spécifiques dans `/api_server/adh6/*/storage/`

#### Logique métier

- Managers correspondants dans `/api_server/adh6/*/`

#### Interface utilisateur

- Composants Angular dans `/frontend_angular/src/app/`
- Styles globaux dans `/frontend_angular/src/styles.scss`

#### Configuration

- Backend : `/api_server/adh6/config/`
- Frontend : `/frontend_angular/src/environments/`
- Docker : Fichiers Docker-compose à la racine

### Debugging et tests

- Tests backend : Exécutez `pytest` dans le dossier `/api_server/`
- Tests frontend : Exécutez `ng test` dans le dossier `/frontend_angular/`
- Logs : Les logs sont générés dans la console Docker et dans les fichiers de log configurés

## Conclusion

ADH6 est une application complexe mais bien structurée suivant les principes de la Clean Architecture côté backend et une architecture modulaire côté frontend. Cette séparation des préoccupations facilite la maintenance et l'évolution de l'application.
