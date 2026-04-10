import os
from datetime import datetime, timedelta

os.environ["ENVIRONMENT"] = "testing"
os.environ["TESTING"] = "1"
# Set test Keycloak environment variables
os.environ["KEYCLOAK_URL"] = "https://keycloak.minet.net"
os.environ["KEYCLOAK_REALM"] = "MiNET"
os.environ["KEYCLOAK_CLIENT_ID"] = "adh6-testing"
os.environ["KEYCLOAK_CLIENT_SECRET"] = "hSK6bC7s4gwnwd7td2iys4Aljgafuy5O"
os.environ["TOKENINFO_FUNC"] = "test.auth.oidc_info"

# os.environ["TOKENINFO_FUNC"] = "test.auth.token_info"
# Import FastAPI app
from adh6.main import app  # noqa


tomorrow = datetime.now().date() + timedelta(days=1)
