from typing import Any, Dict

from adh6.authentication.security import Roles

TESTING_CLIENT = 'TestingClient'
SAMPLE_CLIENT = 'SampleMember'

def token_info(token) -> Dict[str, Any]:
    print(token)
    if token == "TEST_TOKEN":
        return {
            "uid": TESTING_CLIENT,
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
            "uid": SAMPLE_CLIENT,
            "scope": [
                Roles.USER.value
            ]
        }

