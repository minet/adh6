import os
from datetime import timedelta

from adh6.datetime_utils import utc_today

os.environ["ENVIRONMENT"] = "testing"
os.environ["TESTING"] = "1"
os.environ["OIDC_ISSUER"] = "https://keycloak.minet.net/realms/MiNET"
os.environ["OIDC_CLIENT_ID"] = "adh6-testing"

# Import FastAPI app
from adh6.main import app  # noqa

# Keep date-based fixtures in the future even when the test suite crosses
# midnight. They must still remain within the "next week" filter window.
tomorrow = utc_today() + timedelta(days=2)
