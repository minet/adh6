from typing import Any, Dict

from adh6.authentication.security import Roles

TESTING_CLIENT = 'TestingClient'
SAMPLE_CLIENT = 'SampleClient'
SAMPLE_CLIENT2 = 'SampleClient2'

def token_info(token) -> Dict[str, Any]:
    return {
        "uid": TESTING_CLIENT if token == "TEST_TOKEN" else (SAMPLE_CLIENT if token == "TEST_TOKEN_SAMPLE" else SAMPLE_CLIENT2),
        "scope": ["profile"],
        "groups": [
            Roles.SUPERADMIN.value,
            Roles.ADMIN.value,
            Roles.ADMIN.TRESO.value,
            Roles.USER.value,
            Roles.VLAN_DEV.value,
            Roles.VLAN_HOSTING.value,
            Roles.VLAN_PROD.value
        ] if token == "TEST_TOKEN" else []
    }
