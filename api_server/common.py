#!/usr/bin/env python3
import os

import connexion
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import CONFIGURATION, TEST_CONFIGURATION, MANAGE_CONFIGURATION
from src.interface_adapter.elasticsearch.repository import ElasticSearchRepository
from src.interface_adapter.http_api.account import AccountHandler
from src.interface_adapter.http_api.account_type import AccountTypeHandler
from src.interface_adapter.http_api.bug_report import BugReportHandler
from src.interface_adapter.http_api.caisse import CaisseHandler
from src.interface_adapter.http_api.device import DeviceHandler
from src.interface_adapter.http_api.health import HealthHandler
from src.interface_adapter.http_api.member import MemberHandler
from src.interface_adapter.http_api.payment_method import PaymentMethodHandler
from src.interface_adapter.http_api.port import PortHandler
from src.interface_adapter.http_api.product import ProductHandler
from src.interface_adapter.http_api.room import RoomHandler
from src.interface_adapter.http_api.stats import StatsHandler
from src.interface_adapter.http_api.switch import SwitchHandler
from src.interface_adapter.http_api.temporary_account import TemporaryAccountHandler
from src.interface_adapter.http_api.transaction import TransactionHandler
from src.interface_adapter.snmp.switch_network_manager import SwitchSNMPNetworkManager
from src.interface_adapter.sql.account_repository import AccountSQLRepository
from src.interface_adapter.sql.account_type_repository import AccountTypeSQLRepository
from src.interface_adapter.sql.caisse_repository import CaisseSQLRepository
from src.interface_adapter.sql.device_repository import DeviceSQLRepository
from src.interface_adapter.sql.member_repository import MemberSQLRepository
from src.interface_adapter.sql.model.database import Database
from src.interface_adapter.sql.money_repository import MoneySQLRepository
from src.interface_adapter.sql.network_object_repository import NetworkObjectSQLRepository
from src.interface_adapter.sql.payment_method_repository import PaymentMethodSQLRepository
from src.interface_adapter.sql.ping_repository import PingSQLRepository
from src.interface_adapter.sql.product_repository import ProductSQLRepository
from src.interface_adapter.sql.room_repository import RoomSQLRepository
from src.interface_adapter.sql.transaction_repository import TransactionSQLRepository
from src.resolver import ADHResolver
from src.use_case.account_manager import AccountManager
from src.use_case.account_type_manager import AccountTypeManager
from src.use_case.bug_report_manager import BugReportManager
from src.use_case.caisse_manager import CaisseManager
from src.use_case.device_manager import DeviceManager
from src.use_case.health_manager import HealthManager
from src.use_case.member_manager import MemberManager
from src.use_case.payment_method_manager import PaymentMethodManager
from src.use_case.port_manager import PortManager
from src.use_case.product_manager import ProductManager
from src.use_case.room_manager import RoomManager
from src.use_case.switch_manager import SwitchManager
from src.use_case.transaction_manager import TransactionManager

# THIS IMPORT IS NEEDED
# from src.interface_adapter.sql.model.models import *
#
from src.interface_adapter.sql.model.models import *


def init(testing=True, managing=False):
    """
    Initialize and wire together the dependency of the application.
    """
    if testing:
        configuration = TEST_CONFIGURATION
    elif managing:
        configuration = MANAGE_CONFIGURATION
    else:
        configuration = CONFIGURATION

    Database.init_db(configuration.DATABASE, testing=testing)

    # Repositories:
    ping_repository = PingSQLRepository()
    member_sql_repository = MemberSQLRepository()
    network_object_sql_repository = NetworkObjectSQLRepository()
    device_sql_repository = DeviceSQLRepository()
    room_sql_repository = RoomSQLRepository()
    elk_repository = ElasticSearchRepository(configuration)
    money_repository = MoneySQLRepository()
    switch_network_manager = SwitchSNMPNetworkManager()
    account_sql_repository = AccountSQLRepository()
    product_sql_repository = ProductSQLRepository()
    payment_method_sql_repository = PaymentMethodSQLRepository()
    transaction_sql_repository = TransactionSQLRepository()
    account_type_sql_repository = AccountTypeSQLRepository()
    caisse_sql_repository = CaisseSQLRepository()

    # Managers
    health_manager = HealthManager(ping_repository)
    switch_manager = SwitchManager(
        switch_repository=network_object_sql_repository,
    )
    port_manager = PortManager(
        port_repository=network_object_sql_repository,
    )
    device_manager = DeviceManager(
        device_repository=device_sql_repository,
        member_repository=member_sql_repository,
        room_repository=room_sql_repository,
        vlan_repository=network_object_sql_repository,
        ip_allocator=device_sql_repository,
    )
    member_manager = MemberManager(
        member_repository=member_sql_repository,
        money_repository=money_repository,
        membership_repository=member_sql_repository,
        logs_repository=elk_repository,
        device_repository=device_sql_repository,
        configuration=configuration,
    )
    room_manager = RoomManager(
        room_repository=room_sql_repository,
    )
    account_manager = AccountManager(
        account_repository=account_sql_repository,
        member_repository=member_sql_repository,
    )
    product_manager = ProductManager(
        product_repository=product_sql_repository,
    )

    payment_method_manager = PaymentMethodManager(
        payment_method_repository=payment_method_sql_repository
    )
    transaction_manager = TransactionManager(
        transaction_repository=transaction_sql_repository,
    )
    account_type_manager = AccountTypeManager(
        account_type_repository=account_type_sql_repository
    )
    caisse_manager = CaisseManager(
        caisse_repository=caisse_sql_repository,
        transaction_repository=transaction_sql_repository
    )
    bug_report_manager = BugReportManager(configuration.GITLAB_CONF, testing=testing)

    # HTTP Handlers:
    health_handler = HealthHandler(health_manager)
    stats_handler = StatsHandler(transaction_manager, device_manager, member_manager)
    transaction_handler = TransactionHandler(transaction_manager, payment_method_manager, caisse_manager)
    member_handler = MemberHandler(member_manager)
    device_handler = DeviceHandler(device_manager)
    room_handler = RoomHandler(room_manager)
    switch_handler = SwitchHandler(switch_manager)
    port_handler = PortHandler(port_manager, switch_manager, switch_network_manager)
    temporary_account_handler = TemporaryAccountHandler()
    account_type_handler = AccountTypeHandler(account_type_manager)
    payment_method_handler = PaymentMethodHandler(payment_method_manager)
    account_handler = AccountHandler(account_manager, transaction_manager)
    product_handler = ProductHandler(product_manager)
    bug_report_handler = BugReportHandler(bug_report_manager)
    caisse_handler = CaisseHandler(caisse_manager)

    # Connexion will use this function to authenticate and fetch the information of the user.
    if os.environ.get('TOKENINFO_FUNC') is None:
        os.environ['TOKENINFO_FUNC'] = 'src.interface_adapter.http_api.auth.token_info'

    app = connexion.FlaskApp(__name__, specification_dir='openapi')
    app.add_api('swagger.yaml',
                # resolver=RestyResolver('src.interface_adapter.http_api'),
                resolver=ADHResolver({
                    'health': health_handler,
                    'stats': stats_handler,
                    'transaction': transaction_handler,
                    'member': member_handler,
                    'device': device_handler,
                    'room': room_handler,
                    'switch': switch_handler,
                    'port': port_handler,
                    'temporary_account': temporary_account_handler,
                    'account_type': account_type_handler,
                    'payment_method': payment_method_handler,
                    'account': account_handler,
                    'product': product_handler,
                    'bug_report': bug_report_handler,
                    'caisse': caisse_handler,
                }),
                validate_responses=True,
                strict_validation=True,
                pythonic_params=True,
                auth_all_paths=True,
                )

    app.app.config.update(configuration.API_CONF)

    app.app.config.update(configuration.DATABASE)
    app.app.config.update({'SQLALCHEMY_DATABASE_URI': configuration.DATABASE["drivername"] + "://" + configuration.DATABASE[
        'username'] + ":" + configuration.DATABASE["password"] + '@' + configuration.DATABASE['host'] + '/' + \
                                            configuration.DATABASE['database']})
    db = SQLAlchemy(app.app)
    migrate = Migrate(app.app, db)

    return app, migrate