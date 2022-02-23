from src.interface_adapter.http_api.auth import token_info
from test.integration.context import app


def test_token_info_testing():
    with app.app.test_request_context():
        assert token_info("IGNORED") == {
            'uid': 'TestingClient', 
            'scope': ['profile'],
            'groups': [
                "adh6_user", 
                "adh6_admin", 
                "adh6_treso",
                "adh6_superadmin",
                "cluster-dev",
                "cluster-prod",
                "cluster-hosting"
            ]
        }
