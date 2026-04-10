import os
from enum import Enum


class Method(Enum):
    READ = 0
    WRITE = 1


# NOTE: Old Connexion-based auth functions removed.
# For FastAPI, authentication is handled via middleware and route dependencies.
# Reference: adh6/main.py for exception handlers and routing.


user_id = "preferred_username" if "keycloak" in os.environ.get("OAUTH2_BASE_PATH", "http://localhost") else "id"
