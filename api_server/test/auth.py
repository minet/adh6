from typing import Any, Dict

TESTING_CLIENT = 'TestingClient'
SAMPLE_CLIENT = 'SampleClient'
SAMPLE_CLIENT2 = 'SampleClient2'

def token_info(token) -> Dict[str, Any]:
    return {
        "uid": TESTING_CLIENT if token == "TEST_TOKEN" else (SAMPLE_CLIENT if token == "TEST_TOKEN_SAMPLE" else SAMPLE_CLIENT2),
        "scope": ["profile"],
        "groups": [
            "adh6_user",
            "adh6_admin",
            "adh6_treso",
            "adh6_superadmin",
            "cluster-dev",
            "cluster-prod",
            "cluster-hosting"
        ] if token == "TEST_TOKEN" else []
    }
