import os

# Ensure test settings are active before any application modules are imported.
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("OIDC_ISSUER", "https://keycloak.minet.net/realms/MiNET")
os.environ.setdefault("OIDC_CLIENT_ID", "adh6-testing")
os.environ.setdefault("SESSION_SECRET", "adh6-testing-session-secret")

TESTING_CLIENT_TOKEN = "TEST_TOKEN"
SAMPLE_CLIENT_TOKEN = "TEST_TOKEN_SAMPLE"
TESTING_CLIENT = "TestingClient"
TESTING_CLIENT_ID = 28
SAMPLE_CLIENT = "SampleMember"
SAMPLE_CLIENT_ID = 31

OIDC_TESTING_USERNAME = "adh6_testing"
OIDC_TESTING_PASSWORD = "adh6_testing_password"
