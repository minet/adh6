from typing import Any, Dict

from adh6.authentication.security import Roles

TESTING_CLIENT = 'TestingClient'
TESTING_CLIENT_ID = 28
SAMPLE_CLIENT = 'SampleMember'
SAMPLE_CLIENT_ID = 31

def token_info(token) -> Dict[str, Any]:
    if token == "TEST_TOKEN":
        return {
            "uid": TESTING_CLIENT_ID,
            "scope": [
                Roles.ADMIN_READ.value,
                Roles.ADMIN_WRITE.value,
                Roles.TRESO_READ.value,
                Roles.TRESO_WRITE.value,
                Roles.USER.value,
                Roles.NETWORK_READ.value,
                Roles.NETWORK_WRITE.value,
                Roles.NETWORK_DEV.value,
                Roles.NETWORK_HOSTING.value,
                Roles.NETWORK_PROD.value
            ]
        }
    else:
        return {
            "uid": SAMPLE_CLIENT_ID,
            "scope": [
                Roles.USER.value
            ]
        }

