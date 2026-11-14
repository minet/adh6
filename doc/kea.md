# Réservations DHCP dans Kea

ADH6 envoie lui-même à Kea les réservations DHCPv4 (MAC vers IP). Kea les écrit dans sa propre base, au schéma Kea standard (`dhcp3` sur fdpsql).
Avant, Kea lisait des vues SQL sur la base d'ADH6 (`dhcp2`). Elles empêchaient `kea-admin db-upgrade` de migrer la base, et rendaient Kea dépendant du schéma d'ADH6.
Côté Kea (config, API, bascule) : voir le dépôt `minet/configurations/push/kea-dhcp`.

Le code est dans `backend/adh6/kea/`.

## Ce qui est réservé

Les règles sont les mêmes que celles des anciennes vues (`kea/reservations.py`) :
- un appareil n'est réservé que si son adhérent est dans une chambre qui a un VLAN, et que l'appareil a une IPv4 ;
- un appareil filaire est réservé dans le sous-réseau dont l'id est le numéro du VLAN ;
- un appareil Wi-Fi est réservé dans le sous-réseau du /28 de l'adhérent dans `10.42.0.0/16`. L'id vaut 1000 pour `10.42.0.16/28`, puis augmente de 1 à chaque /28 suivant (mêmes ids que `nat-wifi.conf`) ;
- un routeur (table `routeurs`, jamais écrite par ADH6) est réservé dans le sous-réseau 4242.

Le DHCPv6 n'est pas utilisé : rien n'est envoyé pour l'IPv6.

## Quand ADH6 écrit dans Kea

1. **Pendant la requête**, les repositories marquent ce qu'ils touchent (`kea/tracker.py`) :
   - les adhérents dont un appareil, l'IP, le /28 ou la chambre change ;
   - les MAC d'un appareil supprimé ou d'une MAC modifiée ;
   - les membres d'une chambre supprimée ou qui change de VLAN.
2. **Après le commit**, `get_session` appelle `kea/sync.py`. Pour chaque MAC concernée, ADH6 lit ce que Kea contient (`reservation-get-by-id`), puis supprime et ajoute ce qu'il faut (`reservation-del`, `reservation-add`). Les suppressions passent avant les ajouts. Une requête annulée (rollback) n'envoie rien.
3. **Chaque nuit**, `python -m adh6.kea.reconcile` compare toutes les réservations de Kea (`reservation-get-page`) avec ADH6 et corrige les écarts.
   - Il supprime aussi ce qui a été ajouté à la main dans Kea.
   - `--dry-run` liste les changements sans les faire.
   - `--kea-url` vise un autre Kea, par exemple celui de la préprod.
   - Code de sortie : 0 si Kea correspond à ADH6, 1 si un changement a échoué ou si deux appareils ont la même MAC dans un sous-réseau, 2 si Kea ou la configuration est inutilisable.

Si Kea ne répond pas ou refuse une commande, la modification reste enregistrée dans ADH6. Le problème est journalisé (`kea_sync_failed`, `kea_reservation_add_failed`…), et la resynchronisation de la nuit corrige Kea.
La synchronisation après commit est limitée à `KEA_SYNC_BUDGET_SECONDS`, puisqu'elle passe avant l'envoi de la réponse.

## Configuration

| Variable | Défaut | Rôle |
|---|---|---|
| `KEA_ENABLED` | `false` | Active la synchronisation après commit (la commande de resynchronisation ne la demande pas) |
| `KEA_API_URLS` | | URL de l'API, séparées par des virgules, kea1 puis kea2 : `https://192.168.102.28:8443/,https://192.168.102.68:8443/` |
| `KEA_API_USER` | `adh6` | Utilisateur de l'API |
| `KEA_API_PASSWORD` | | Mot de passe de l'API (la variable CI `KEA_API_PASSWORD` du dépôt kea-dhcp) |
| `KEA_API_CA_FILE` | | Fichier PEM avec les certificats autosignés de kea1 et kea2, l'un après l'autre |
| `KEA_API_TIMEOUT_SECONDS` | `5` | Délai par requête |
| `KEA_SYNC_BUDGET_SECONDS` | `10` | Durée maximale de la synchronisation après un commit |

Le client essaie les URL dans l'ordre et garde la première qui répond : kea1 et kea2 lisent la même base.

**Le compte de l'API peut lancer toutes les commandes Kea**, pas seulement les réservations : Kea n'a pas le hook RBAC qui permettrait de le limiter. Le mot de passe doit être traité comme un accès root au DHCP.

## Mise en service

L'ordre complet est dans le README du dépôt kea-dhcp. Côté ADH6 :
1. Déployer avec `KEA_ENABLED=true` et les variables ci-dessus, une fois Kea passé sur `dhcp3`.
2. Lancer tout de suite `python -m adh6.kea.reconcile --dry-run`, puis sans `--dry-run`. Ça rattrape ce qui a changé depuis la copie initiale des réservations.
3. Planifier la resynchronisation chaque nuit, avec un service cron dans le dépôt swarm-prod.
