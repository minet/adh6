#!/usr/bin/env python3
import os
from typing import Tuple

from connexion.apps.flask_app import FlaskApp
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import CONFIGURATION, TEST_CONFIGURATION

from src.resolver import ADHResolver
from src.interface_adapter.http_api import (
    BugReportHandler,
    DeviceHandler,
    HealthHandler,
    MemberHandler,
    PortHandler,
    ProfileHandler,
    StatsHandler,
    TransactionHandler,
    TreasuryHandler,
    VLANHandler,
    AccountHandler,
    PaymentMethodHandler,
    ProductHandler,
    RoomHandler,
    SwitchHandler
)

from src.interface_adapter.sql.model.database import Database

def init(testing=True) -> Tuple[FlaskApp, Migrate]:
    """
    Initialize and wire together the dependency of the application.
    """
    if testing:
        configuration = TEST_CONFIGURATION
    else:
        configuration = CONFIGURATION

    Database.init_db(configuration.DATABASE, testing=testing)

    # Connexion will use this function to authenticate and fetch the information of the user.
    if os.environ.get('TOKENINFO_FUNC') is None:
        os.environ['TOKENINFO_FUNC'] = 'src.interface_adapter.http_api.auth.token_info'

    from dependency_injection import get_obj_graph

    obj_graph = get_obj_graph(configuration, testing)

    app = FlaskApp(__name__, specification_dir='openapi')
    app.add_api(
        'swagger.yaml',
        resolver=ADHResolver({
            'health': obj_graph.provide(HealthHandler),
            'stats': obj_graph.provide(StatsHandler),
            'profile': obj_graph.provide(ProfileHandler),
            'transaction': obj_graph.provide(TransactionHandler),
            'member': obj_graph.provide(MemberHandler),
            'device': obj_graph.provide(DeviceHandler),
            'room': obj_graph.provide(RoomHandler),
            'switch': obj_graph.provide(SwitchHandler),
            'port': obj_graph.provide(PortHandler),
            'account_type': obj_graph.provide(AccountHandler),
            'payment_method': obj_graph.provide(PaymentMethodHandler),
            'account': obj_graph.provide(AccountHandler),
            'product': obj_graph.provide(ProductHandler),
            'bug_report': obj_graph.provide(BugReportHandler),
            'treasury': obj_graph.provide(TreasuryHandler),
            'vlan': obj_graph.provide(VLANHandler)
        }),
        validate_responses=True,
        strict_validation=True,
        pythonic_params=True,
        auth_all_paths=True,
    )

    app.app.config.update(configuration.API_CONF)
    app.app.config.update(configuration.DATABASE)
    if 'username' in configuration.DATABASE:
        app.app.config.update({
            'SQLALCHEMY_DATABASE_URI': f'{configuration.DATABASE["drivername"]}://{configuration.DATABASE["username"]}:{configuration.DATABASE["password"]}@{configuration.DATABASE["host"]}/{configuration.DATABASE["database"]}'
        })
    else:
        app.app.config.update({
            'SQLALCHEMY_DATABASE_URI': f'{configuration.DATABASE["drivername"]}://{configuration.DATABASE["database"]}'
        })

    app.app.config['SESSION_TYPE'] = 'memcached'
    app.app.config['SECRET_KEY'] = 'TODO A CHANGER' #@TODO

    database = SQLAlchemy(app.app)

    return app, Migrate(app.app, database)
