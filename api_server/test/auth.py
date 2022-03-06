from typing import Any, Dict

TESTING_CLIENT = 'TestingClient'

def token_info(_) -> Dict[str, Any]:
    return {
        "uid": TESTING_CLIENT,
        "scope": ["profile"],
        "groups": [
            "adh6_user",
            "adh6_admin",
            "adh6_treso",
            "adh6_superadmin",
            "cluster-dev",
            "cluster-prod",
            "cluster-hosting"
        ]
    }
