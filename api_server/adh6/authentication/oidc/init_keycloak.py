from connexion import FlaskApp
from keycloak import KeycloakOpenID

import os


def init_keycloak(app: FlaskApp) -> KeycloakOpenID:
    required_env_vars = ["KEYCLOAK_URL", "KEYCLOAK_REALM", "KEYCLOAK_CLIENT_ID", "KEYCLOAK_CLIENT_SECRET"]
    missing_vars = [var for var in required_env_vars if var not in os.environ]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    # Initialize Keycloak OpenID client with environment variables
    keycloak_url = os.environ.get("KEYCLOAK_URL")
    realm_name = os.environ.get("KEYCLOAK_REALM")
    client_id = os.environ.get("KEYCLOAK_CLIENT_ID")
    client_secret = os.environ.get("KEYCLOAK_CLIENT_SECRET")

    keycloak_openid = KeycloakOpenID(
        server_url=keycloak_url, client_id=client_id, realm_name=realm_name, client_secret_key=client_secret
    )

    app.app.config["KEYCLOAK_CLIENT"] = keycloak_openid
    app.app.config["KEYCLOAK_WELL_KNOWN"] = keycloak_openid.well_known()

    return keycloak_openid
