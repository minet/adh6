import os
from adh6.member.notification_manager import NotificationManager
import connexion
import pinject
import abc

from connexion.apps.flask_app import FlaskApp
from flask_migrate import Migrate
from adh6.member.storage.notification_template_repository import NotificationTemplateSQLRepository

from adh6.resolver import ADHResolver
from adh6.treasury.http import *
from adh6.member.http import *
from adh6.device.http import DeviceHandler
from adh6.metrics.http import HealthHandler
from adh6.network.http import PortHandler, SwitchHandler
from adh6.subnet.http import VLANHandler
from adh6.room.http import RoomHandler
from adh6.authentication.http import ApiKeyHandler, RoleHandler

from adh6.storage import db

handlers = [
    AccountHandler,
    AccountTypeHandler,
    PaymentMethodHandler,
    ProductHandler,
    RoomHandler,
    SwitchHandler,
    HealthHandler,
    ProfileHandler,
    TransactionHandler,
    MemberHandler,
    DeviceHandler,
    PortHandler,
    TreasuryHandler,
    VLANHandler,
    ApiKeyHandler,
    RoleHandler,
    MailinglistHandler,
    CharterHandler
]

from adh6.treasury import (
    AccountManager, 
    AccountTypeManager, 
    CashboxManager, 
    TransactionManager, 
    ProductManager, 
    PaymentMethodManager,
    init as treasury_init
)
from adh6.member import (
    MemberManager, 
    MailinglistManager, 
    CharterManager, 
    SubscriptionManager
)
from adh6.device import (
    DeviceManager, 
    DeviceIpManager, 
    DeviceLogsManager
)
from adh6.default import CRUDManager, CRUDRepository, DefaultHandler
from adh6.metrics import HealthManager
from adh6.network import PortManager, SwitchManager
from adh6.room import RoomManager
from adh6.subnet import VlanManager
from adh6.authentication import (
    ApiKeyManager, 
    RoleManager,
    init as authentication_init
)

managers = [
    DeviceManager,
    DeviceIpManager,
    DeviceLogsManager,
    HealthManager,
    ProductManager,
    CashboxManager,
    AccountTypeManager,
    AccountManager,
    TransactionManager,
    PaymentMethodManager,
    MemberManager,
    RoomManager,
    PortManager,
    SwitchManager,
    VlanManager,
    ApiKeyManager,
    RoleManager,
    MailinglistManager,
    CharterManager,
    NotificationManager,
    SubscriptionManager,
]

from adh6.treasury.storage import (
    TransactionRepository, 
    AccountRepository, 
    PaymentMethodRepository, 
    AccountTypeRepository, 
    CashboxRepository,
    ProductRepository
)
from adh6.member.storage import (
    MembershipRepository,
    MemberRepository,
    MailinglistReposiroty,
    CharterRepository,
)
from adh6.member.smtp import NotificationRepository
from adh6.device.storage import (
    DeviceRepository,
    IPAllocator,
    LogsRepository
)
from adh6.authentication.storage import (
    RoleRepository,
    ApiKeyRepository
)
from adh6.metrics.storage import PingRepository
from adh6.network.storage import PortRepository, SwitchRepository
from adh6.subnet.storage import VLANRepository
from adh6.room.storage import RoomRepository
from adh6.network.snmp import SwitchNetworkManager


config = {
    'production': 'adh6.config.configuration.ProductionConfig',
    'development': 'adh6.config.configuration.DevelopmentConfig',
    'testing': 'adh6.config.configuration.TestingConfig'
}


def get_obj_graph():
    _global = managers+ \
        handlers+ \
        [SwitchNetworkManager]+ \
        [TransactionRepository, AccountTypeRepository, AccountRepository, PaymentMethodRepository, CashboxRepository, ProductRepository]+ \
        [SubscriptionManager, MemberRepository, MembershipRepository, MailinglistReposiroty, CharterRepository, NotificationRepository, NotificationTemplateSQLRepository ] + \
        [DeviceRepository, IPAllocator, LogsRepository] + \
        [PingRepository, VLANRepository, RoomRepository] + \
        [PortRepository, SwitchRepository] + \
        [RoleRepository, ApiKeyRepository]

    _base_interfaces = [
        abc.ABC,
        CRUDManager,
        CRUDRepository,
        DefaultHandler,
        object
    ]

    def get_base_class(cls):
        if len(cls.__bases__) == 0 or set(_base_interfaces)&set(cls.__bases__):
            return cls
        return get_base_class(cls.__bases__[0])

    _class_name_to_abstract = {
        cls.__name__: get_base_class(cls) for cls in _global
    }

    def get_arg_names(class_name):
        if class_name in _class_name_to_abstract:
            class_name = _class_name_to_abstract[class_name].__name__
        return pinject.bindings.default_get_arg_names_from_class_name(class_name)

    return pinject.new_object_graph(
        modules=None,
        classes=_global,
        get_arg_names_from_class_name=get_arg_names
    )


def init(testing: bool = False) -> FlaskApp:
    environment = os.environ.get('ENVIRONMENT', 'default').lower()
    if environment == "default" or environment not in config:
        raise EnvironmentError("The server cannot be started because environment variable has not been set or is not production, development, testing")

    # Connexion will use this function to authenticate and fetch the information of the user.
    os.environ['TOKENINFO_FUNC'] = os.environ.get('TOKENINFO_FUNC', 'adh6.authentication.token_info')
    os.environ['APIKEYINFO_FUNC'] = os.environ.get('APIKEYINFO_FUNC', 'adh6.authentication.apikey_auth')

    # Initialize the application
    app = connexion.App(__name__, specification_dir='../openapi')

    if app.app is None:
        raise Exception("Error when setting the flask application")

    # Setup the configuration
    app.app.config.from_object(config[environment])

    app.app.app_context().push()
    obj_graph = get_obj_graph()

    app.add_api(
        'swagger.yaml',
        resolver=ADHResolver(
            {
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
                'vlan': obj_graph.provide(VLANHandler),
                'role': obj_graph.provide(RoleHandler),
                'api_keys': obj_graph.provide(ApiKeyHandler),
                'mailinglist': obj_graph.provide(MailinglistHandler),
                'charter': obj_graph.provide(CharterHandler)
            }
        ),
        validate_responses=True,
        strict_validation=True,
        pythonic_params=True,
        auth_all_paths=True,
    )

    from .logging import setup_login
    setup_login()
    db.init_app(app.app)
    Migrate(app.app, db)

    return app
