# Environnement local

Fichiers utilisés uniquement en développement local, jamais en CI ni en prod.

| Fichier | Rôle |
|---|---|
| `seed.sql` | Données de dev, appliquées par le service `database_seed` à chaque `docker compose up` |
| `snmpsim/` | Switch Cisco simulé en SNMP (service `snmpsim`), valeurs dans `data/adh6.snmprec` |

À la racine, également réservés au local : `compose.yaml`, `compose.debug-api.yaml`, `Makefile`.

## Démarrage

```sh
make run-dev   # ou docker compose up, une fois le JAR Keycloak construit (make keycloak-jar)
```

Aucun `.env` n'est nécessaire : les valeurs par défaut sont dans `compose.yaml`.

Le frontend tourne avec deux dev servers Angular, un par langue : https://localhost/fr/ et https://localhost/en/.

Prérequis : cloner `fdpuserstoragefederation` et `theme` à côté de ce dépôt (Keycloak local).

## Comptes

| Login | Mot de passe | Rôles |
|---|---|---|
| `admin` | `admin` | admin, trésorerie, réseau |
| `adherent` | `adherent` | utilisateur |

Console Keycloak : http://localhost:8180/admin (`admin` / `admin`).
