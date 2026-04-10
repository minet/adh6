import os

from fastapi import FastAPI
from keycloak import KeycloakOpenID


def init_keycloak(app: FastAPI) -> KeycloakOpenID:
    required_env_vars = ["KEYCLOAK_URL", "KEYCLOAK_REALM", "KEYCLOAK_CLIENT_ID", "KEYCLOAK_CLIENT_SECRET"]
    missing_vars = [var for var in required_env_vars if var not in os.environ]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    # Initialize Keycloak OpenID client with environment variables
    keycloak_url = os.environ["KEYCLOAK_URL"]
    realm_name = os.environ["KEYCLOAK_REALM"]
    client_id = os.environ["KEYCLOAK_CLIENT_ID"]
    client_secret = os.environ["KEYCLOAK_CLIENT_SECRET"]

    keycloak_openid = KeycloakOpenID(
        server_url=keycloak_url, client_id=client_id, realm_name=realm_name, client_secret_key=client_secret
    )

    app.state.KEYCLOAK_CLIENT = keycloak_openid

    # Only try to fetch well-known configuration if not in testing environment
    app.state.KEYCLOAK_WELL_KNOWN = keycloak_openid.well_known()

    return keycloak_openid
