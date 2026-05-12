import os

# Ensure test settings are active before any application modules are imported.
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("KEYCLOAK_URL", "https://keycloak.minet.net")
os.environ.setdefault("KEYCLOAK_REALM", "MiNET")
os.environ.setdefault("KEYCLOAK_CLIENT_ID", "adh6-testing")
os.environ.setdefault("KEYCLOAK_CLIENT_SECRET", "adh6-testing-secret")
os.environ.setdefault("TOKENINFO_FUNC", "test.auth.oidc_info")
os.environ.setdefault("NETBOX_ENABLED", "false")

TESTING_CLIENT_TOKEN = "TEST_TOKEN"
SAMPLE_CLIENT_TOKEN = "TEST_TOKEN_SAMPLE"
TESTING_CLIENT = "TestingClient"
TESTING_CLIENT_ID = 28
SAMPLE_CLIENT = "SampleMember"
SAMPLE_CLIENT_ID = 31

OIDC_TESTING_USERNAME = "adh6_testing"
OIDC_TESTING_PASSWORD = "adh6_testing_password"
