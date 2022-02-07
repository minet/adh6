from src.interface_adapter.http_api.auth import token_info
from src.interface_adapter.sql.model.models import db
from test.integration.context import app


def api_client():
    with app.app.test_client() as c:
        db.create_all()
        s = db.session()
        s.commit()
        yield c
        db.session.remove()
        db.drop_all()


def test_token_info_testing(api_client):
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
