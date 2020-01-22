import pytest

from config.TEST_CONFIGURATION import DATABASE as db_settings
from src.interface_adapter.http_api.auth import token_info
from src.interface_adapter.sql.model.database import Database as db
from test.integration.context import app


def api_client():
    with app.app.test_client() as c:
        db.init_db(db_settings, testing=True)
        s = db.get_db().get_session()

        s.commit()

        yield c


def test_token_info_testing(api_client):
    with app.app.test_request_context():
        assert token_info("IGNORED") == {'uid': 'TestingClient', 'scope': ['profile'], 'groups': []}
