#!/usr/bin/env python3
import os
import connexion

from connexion.apps.flask_app import FlaskApp
from flask_migrate import Migrate

from src.resolver import ADHResolver
from src.plugins.treasury.interface_adapters.http import *
from src.plugins.member.interface_adapters.http import *
from src.plugins.device.interface_adapters.http import *
from src.plugins.metrics.interface_adapters.http.health import HealthHandler
from src.plugins.network.interface_adapters.http.port import PortHandler
from src.plugins.subnet.interface_adapters.http.vlan import VLANHandler
from src.plugins.room.interface_adapters.http.room import RoomHandler
from src.plugins.network.interface_adapters.http.switch import SwitchHandler

from src.interface_adapter.sql.model.models import db
from src.interface_adapter.http_api.auth import cache

config = {
    'production': 'config.configuration.ProductionConfig',
    'development': 'config.configuration.DevelopmentConfig',
    'testing': 'config.configuration.TestingConfig'
}


def init() -> FlaskApp:
    environment = os.environ.get('ENVIRONMENT', 'default').lower()
    if environment == "default" or environment not in config:
        raise EnvironmentError("The server cannot be started because environment variable has not been set or is not production, development, testing")

    # Connexion will use this function to authenticate and fetch the information of the user.
    os.environ['TOKENINFO_FUNC'] = os.environ.get('TOKENINFO_FUNC', 'src.interface_adapter.http_api.auth.token_info')
    os.environ['APIKEYINFO_FUNC'] = os.environ.get('APIKEYINFO_FUNC', 'src.interface_adapter.http_api.auth.apikey_auth')

    # Initialize the application
    app = connexion.App(__name__, specification_dir='openapi')

    if app.app is None:
        raise Exception("Error when setting the flask application")

    # Setup the configuration
    app.app.config.from_object(config[environment])

    from dependency_injection import get_obj_graph
    app.app.app_context().push()
    obj_graph = get_obj_graph()
    app.add_api(
        'swagger.yaml',
        resolver=ADHResolver({
            'health': obj_graph.provide(HealthHandler),
            'profile': obj_graph.provide(ProfileHandler),
            'transaction': obj_graph.provide(TransactionHandler),
            'member': obj_graph.provide(MemberHandler),
            'device': obj_graph.provide(DeviceHandler),
            'room': obj_graph.provide(RoomHandler),
            'switch': obj_graph.provide(SwitchHandler),
            'port': obj_graph.provide(PortHandler),
            'account_type': obj_graph.provide(AccountTypeHandler),
            'payment_method': obj_graph.provide(PaymentMethodHandler),
            'account': obj_graph.provide(AccountHandler),
            'product': obj_graph.provide(ProductHandler),
            'treasury': obj_graph.provide(TreasuryHandler),
            'vlan': obj_graph.provide(VLANHandler)
        }),
        validate_responses=True,
        strict_validation=True,
        pythonic_params=True,
        auth_all_paths=True,
    )

    db.init_app(app.app)
    cache.init_app(app.app, config={'CACHE_TYPE': 'SimpleCache'})

    
    Migrate(app.app, db)

    return app
