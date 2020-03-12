#!/usr/bin/env python3
import os

import connexion
from authlib.integrations.flask_client import OAuth
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import CONFIGURATION, TEST_CONFIGURATION
from src.interface_adapter.http_api.oauth2 import OAuthHandler
from src.interface_adapter.sql.member_repository import MemberSQLRepository
from src.interface_adapter.sql.model.database import Database
from src.interface_adapter.sql.oauth_repository import OAuthSQLRepository
from src.resolver import RegResolver
from src.use_case.oauth_manager import OAuthManager


def init(testing=True, managing=False):
    """
    Initialize and wire together the dependency of the application.
    """
    if testing:
        configuration = TEST_CONFIGURATION
    else:
        configuration = CONFIGURATION

    Database.init_db(configuration.DATABASE, testing=testing)

    oauth = OAuth()

    # Repositories:
    member_sql_repository = MemberSQLRepository()
    oauth_sql_repository = OAuthSQLRepository()

    # Managers
    oauth_manager = OAuthManager(
        oauth_repository=oauth_sql_repository,
        member_repository=member_sql_repository,
        oauth=oauth
    )

    # HTTP Handlers:
    oauth_handler = OAuthHandler(oauth_manager)

    # Connexion will use this function to authenticate and fetch the information of the user.
    if os.environ.get('TOKENINFO_FUNC') is None:
        os.environ['TOKENINFO_FUNC'] = 'src.interface_adapter.http_api.auth.token_info'

    app = connexion.FlaskApp(__name__, specification_dir='openapi')
    app.add_api('swagger.yaml',
                resolver=RegResolver({
                    'oauth': oauth_handler
                }),
                validate_responses=True,
                strict_validation=True,
                pythonic_params=True,
                auth_all_paths=True,
                )

    app.app.config.update(configuration.API_CONF)

    app.app.config.update(configuration.DATABASE)
    if 'username' in configuration.DATABASE:
        app.app.config.update(
            {'SQLALCHEMY_DATABASE_URI': configuration.DATABASE["drivername"] + "://" + configuration.DATABASE[
                'username'] + ":" + configuration.DATABASE["password"] + '@' + configuration.DATABASE['host'] + '/' + \
                                        configuration.DATABASE['database']})
    else:
        app.app.config.update(
            {'SQLALCHEMY_DATABASE_URI': configuration.DATABASE["drivername"] + "://" + configuration.DATABASE[
                'database']})

    db = SQLAlchemy(app.app)
    migrate = Migrate(app.app, db)
    oauth.init_app(app.app)
    oauth.register('cas',
                   client_id='adh6',
                   client_secret='fs9QZsrkzXyJE6AHnSdH3PFrecH5oF',
                   CAS_CLIENT_SECRET='fs9QZsrkzXyJE6AHnSdH3PFrecH5oF',
                   server_metadata_url='https://cas.minet.net/oidc/.well-known/openid-configuration',
                   client_kwargs={'scope': 'openid profile email'}
                   )
    oauth_manager.init_app(app.app)

    return app, migrate
