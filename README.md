# ADH6

ADH6 est l'outil de gestion des adhérents de [MiNET](https://minet.net) : adhésions et cotisations, appareils et attribution d'IP, chambres, équipements réseau (switches, ports, VLANs) et trésorerie.

Lisez aussi [la page du wiki](https://wiki.minet.net/wiki/services/adh6). Si quelque chose est faux ou manque ici, corrigez-le dans votre prochaine MR.

## Stack

Le **backend** est écrit sous Python 3.11 avec le framework FastAPI afin de rester simple et facile à maintenir. Le **frontend** est sous Angular 20.

## Démarrer en local

Prérequis : Docker doit être installé, et les dépôts `fdpuserstoragefederation` et `theme` doivent être clonés (et à jour !) à côté de adh6 pour avoir une copie fidèle du Keycloak de prod en local. Il faut ensuite les build depuis ici via la commande :

```sh
make run-dev
```

L'application est lancée sur https://localhost (http fonctionne aussi) avec du hot-reload par défaut, avec les comptes `admin` / `admin` et `adherent` / `adherent`. Pour plus de détails : [local/README.md](local/README.md).


## Commandes courantes

| Commande | Effet |
|---|---|
| `make run-dev` | Lance toute la stack locale |
| `make run-debug` | Idem, avec debugpy sur le port 5678 |
| `make seed` | Régénère la db locale |
| `make generate` | Régénère le code depuis `openapi/spec.yaml` |
| `make test-backend` | Lance pytest |
| `make check-backend` | Formatage, lint, typage et tests backend (tox) |
| `make lint-frontend` | Lint et formatage du frontend |

Pour travailler hors conteneurs : `uv sync` dans `backend/`, `yarn install --frozen-lockfile` dans `frontend/`.

## Structure du dépôt

```
backend/          API FastAPI (code dans adh6/, migrations Alembic, tests)
frontend/         Application Angular
openapi/spec.yaml Spécification de l'API, source du code généré
reverse_proxy/    Nginx devant le frontend et l'API
local/            Fichiers réservés au dev local (seed, switch simulé)
doc/              Documentation détaillée
```

Documentation détaillée :

- [doc/principes.md](doc/principes.md) : motivations et pourquoi de l'architecture
- [doc/architecture.md](doc/architecture.md) : backend, modules, authentification, SNMP, frontend
- [doc/developpement.md](doc/developpement.md) : environnement, ajouter une fonctionnalité, migrations, tests
- [doc/adhesions.md](doc/adhesions.md) : statuts et étapes d'une cotisation

## Modifier l'API

1. Modifier `openapi/spec.yaml`.
2. Lancer `make generate` : régénère `backend/adh6/entity/` et `frontend/src/app/api/`, il n'ont pas vocation à être modifiés manuellement.
3. Écrire la route dans le `router.py` du module concerné.

## CI et déploiement

La CI GitLab construit les images, lance `tox -e ci` sur le backend, puis déclenche le déploiement via le dépôt `swarm-prod` :

| Branche | Environnement |
|---|---|
| `dev` | adh6-dev.minet.net |
| `master` | adh6.minet.net |

`compose.yaml`, le `Makefile` et `local/` ne servent qu'au dev local.
