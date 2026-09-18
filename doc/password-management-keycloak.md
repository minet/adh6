# Gestion des mots de passe par Keycloak

Fait le 18 septembre 2026 par psders.

## Périmètre

ADH6 ne valide, ne hache et ne persiste plus les mots de passe lui-même. Un membre demande à Keycloak un
lien `UPDATE_PASSWORD` à durée limitée. Les LDAP avec `admin:write` peuvent encore réinitialiser eux-mêmes les mots de passe des utilisateurs, le mot de passe est ensuite transmis à Keycloak qui en fait le traitement. Ce changement prépare la migration de MD4 vers Argon2 qui sera faite plus tard.

### Membre

1. Le frontend appelle `POST /member/{id}/password-reset`.
2. ADH6 vérifie que l'appelant est le membre concerné ou possède `admin:write`.
3. ADH6 obtient un jeton `client_credentials`.
4. ADH6 recherche exactement le login dans le realm configuré.
5. ADH6 appelle `execute-actions-email` avec uniquement `UPDATE_PASSWORD` et une durée de vie
   de 15 minutes par défaut.
6. Le membre choisit le mot de passe dans Keycloak. Le provider fédéré existant sauvegarde le mdp.

### Administrateur

1. Le frontend appelle `PUT /member/{id}/password` avec le nouveau mot de passe via HTTPS.
2. La route exige `admin:write`.
3. ADH6 transmet le secret à Keycloak sur `reset-password`.
4. Keycloak applique sa politique puis appelle le provider fédéré existant.

## Configuration de production

Dans la console d'administration Keycloak :

1. Créer un client `adh6-service` dans le realm `MiNET`.
2. Activer **Client authentication** et **Service accounts roles**.
3. Désactiver Standard flow et Direct access grants.
4. Donner la permission `realm-management/manage-users` au client.
5. Configurer et tester le SMTP du realm.
6. Placer le client secret dans le env :

```text
KEYCLOAK_ADMIN_URL=https://keycloak.example
KEYCLOAK_ADMIN_REALM=MiNET
KEYCLOAK_ADMIN_CLIENT_ID=adh6-service
KEYCLOAK_ADMIN_CLIENT_SECRET=<secret>
KEYCLOAK_PASSWORD_ACTION_LIFESPAN_SECONDS=900
```