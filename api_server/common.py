#!/usr/bin/env python3
import os
from typing import Tuple

from connexion.apps.flask_app import FlaskApp
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import CONFIGURATION, TEST_CONFIGURATION
from src.entity import (
    AbstractAccount, Account,
    AccountType,
    AbstractPaymentMethod, PaymentMethod,
    AbstractProduct, Product,
    AbstractRoom, Room,
    AbstractSwitch, Switch,

)

from src.resolver import ADHResolver

from src.interface_adapter.elasticsearch.repository import ElasticSearchRepository
from src.interface_adapter.http_api.bug_report import BugReportHandler
from src.interface_adapter.http_api.default import DefaultHandler
from src.interface_adapter.http_api.device import DeviceHandler
from src.interface_adapter.http_api.health import HealthHandler
from src.interface_adapter.http_api.member import MemberHandler
from src.interface_adapter.http_api.port import PortHandler
from src.interface_adapter.http_api.profile import ProfileHandler
from src.interface_adapter.http_api.stats import StatsHandler
from src.interface_adapter.http_api.transaction import TransactionHandler
from src.interface_adapter.http_api.treasury import TreasuryHandler
from src.interface_adapter.http_api.vlan import VLANHandler
from src.interface_adapter.snmp.switch_network_manager import SwitchSNMPNetworkManager

from src.interface_adapter.sql.model.database import Database
from src.interface_adapter.sql.account_repository import AccountSQLRepository
from src.interface_adapter.sql.account_type_repository import AccountTypeSQLRepository
from src.interface_adapter.sql.cashbox_repository import CashboxSQLRepository
from src.interface_adapter.sql.device_repository import DeviceSQLRepository
from src.interface_adapter.sql.ip_allocator import IPSQLAllocator
from src.interface_adapter.sql.member_repository import MemberSQLRepository
from src.interface_adapter.sql.membership_repository import MembershipSQLRepository
from src.interface_adapter.sql.payment_method_repository import PaymentMethodSQLRepository
from src.interface_adapter.sql.ping_repository import PingSQLRepository
from src.interface_adapter.sql.port_repository import PortSQLRepository
from src.interface_adapter.sql.product_repository import ProductSQLRepository
from src.interface_adapter.sql.room_repository import RoomSQLRepository
from src.interface_adapter.sql.switch_repository import SwitchSQLRepository
from src.interface_adapter.sql.transaction_repository import TransactionSQLRepository
from src.interface_adapter.sql.vlan_repository import VLANSQLRepository

from src.use_case.account_manager import AccountManager
from src.use_case.account_type_manager import AccountTypeManager
from src.use_case.bug_report_manager import BugReportManager
from src.use_case.cashbox_manager import CashboxManager
from src.use_case.device_manager import DeviceManager
from src.use_case.health_manager import HealthManager
from src.use_case.member_manager import MemberManager
from src.use_case.payment_method_manager import PaymentMethodManager
from src.use_case.port_manager import PortManager
from src.use_case.product_manager import ProductManager
from src.use_case.room_manager import RoomManager
from src.use_case.stats_manager import StatsManager
from src.use_case.switch_manager import SwitchManager
from src.use_case.transaction_manager import TransactionManager
from src.use_case.vlan_manager import VLANManager

def init_managers(configuration, testing=False) -> Tuple[
    HealthManager,
    StatsManager,
    BugReportManager,
    DeviceManager,
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
    SwitchSNMPNetworkManager,]:
    """This function initialize all the manager when the function init is started

    Args:
        configuration ([type]): Configuration of the application.
                                Whether TESTING_CONFIGURATION or CONFIGURATION
        testing (bool, optional): [description]. Defaults to False.

    Returns:
        0: HealthManager
        1: StatsManager
        2: BugReportManager
        3: DeviceManager
        4: ProductManager
        5: CashboxManager
        6: AccountTypeManager
        7: AccountManager
        8: TransactionManager
        9: PaymentMethodManager
        10: MemberManager
        11: RoomManager
        12: PortManager
        13: SwitchManager
        14: SwitchSNMPNetworkManager
        15: VLANManager
        [All the managers used in the application]
    """
    # Repositories:
    device_sql_repository = DeviceSQLRepository()
    elk_repository = ElasticSearchRepository(configuration)
    account_sql_repository = AccountSQLRepository()
    payment_method_sql_repository = PaymentMethodSQLRepository()
    transaction_sql_repository = TransactionSQLRepository()
    account_type_sql_repository = AccountTypeSQLRepository()

    account_manager = AccountManager(
        account_repository=account_sql_repository,
    )
    payment_method_manager = PaymentMethodManager(
        payment_method_repository=payment_method_sql_repository
    )
    cashbox_manager = CashboxManager(
        cashbox_repository=CashboxSQLRepository(),
        transaction_repository=transaction_sql_repository
    )
    device_manager = DeviceManager(
        device_repository=device_sql_repository,
        ip_allocator=IPSQLAllocator()
    )

    return (
        HealthManager(PingSQLRepository()),
        StatsManager(logs_repository=elk_repository),
        BugReportManager(configuration.GITLAB_CONF, testing=testing),
        device_manager,
        ProductManager(
            product_repository=ProductSQLRepository(),
        ),
        cashbox_manager,
        AccountTypeManager(
            account_type_repository=account_type_sql_repository
        ),
        account_manager,
        TransactionManager(
            transaction_repository=transaction_sql_repository,
            payment_method_manager=payment_method_manager,
            cashbox_manager=cashbox_manager
        ),
        payment_method_manager,
        MemberManager(
            member_repository=MemberSQLRepository(),
            payment_method_repository=payment_method_sql_repository,
            membership_repository=MembershipSQLRepository(),
            logs_repository=elk_repository,
            device_repository=device_sql_repository,
            account_repository=account_sql_repository,
            account_type_repository=account_type_sql_repository,
            transaction_repository=transaction_sql_repository,
            device_manager=device_manager,
            configuration=configuration,
        ),
        RoomManager(
            room_repository=RoomSQLRepository(),
        ),
        PortManager(
            port_repository=PortSQLRepository(),
        ),
        SwitchManager(
            switch_repository=SwitchSQLRepository(),
        ),
        SwitchSNMPNetworkManager(),
        VLANManager(VLANSQLRepository())
    )


def init_handlers(configuration, testing=False):
    managers = init_managers(configuration, testing)
    return (
        DefaultHandler(
            Account,
            AbstractAccount,
            managers[7]
        ),
        DefaultHandler(
            AccountType,
            AccountType,
            managers[6]
        ),
        DefaultHandler(
            PaymentMethod,
            AbstractPaymentMethod,
            managers[9]
        ),
        DefaultHandler(
            Product,
            AbstractProduct,
            managers[4]
        ),
        DefaultHandler(
            Room,
            AbstractRoom,
            managers[11]
        ),
        DefaultHandler(
            Switch,
            AbstractSwitch,
            managers[13]
        ),
        HealthHandler(managers[0]),
        StatsHandler(managers[8], managers[3], managers[10], managers[1]),
        ProfileHandler(managers[10]),
        TransactionHandler(managers[8]),
        MemberHandler(managers[10]),
        DeviceHandler(managers[3]),
        PortHandler(managers[12], managers[13], managers[14]),
        BugReportHandler(managers[2]),
        TreasuryHandler(managers[5], managers[7]),
        VLANHandler(managers[15])
    )


def init(testing=True, managing=True) -> Tuple[FlaskApp, Migrate]:
    """
    Initialize and wire together the dependency of the application.
    """
    if testing:
        configuration = TEST_CONFIGURATION
    else:
        configuration = CONFIGURATION

    Database.init_db(configuration.DATABASE, testing=testing)

    (
        account_handler,
        account_type_handler,
        payment_method_handler,
        product_handler,
        room_handler,
        switch_handler,
        health_handler,
        stats_handler,
        profile_handler,
        transaction_handler,
        member_handler,
        device_handler,
        port_handler,
        bug_report_handler,
        treasury_handler,
        vlan_handler
    ) = init_handlers(configuration, testing)

    # Connexion will use this function to authenticate and fetch the information of the user.
    if os.environ.get('TOKENINFO_FUNC') is None:
        os.environ['TOKENINFO_FUNC'] = 'src.interface_adapter.http_api.auth.token_info'

    app = FlaskApp(__name__, specification_dir='openapi')
    app.add_api(
        'swagger.yaml',
        resolver=ADHResolver({
            'health': health_handler,
            'stats': stats_handler,
            'profile': profile_handler,
            'transaction': transaction_handler,
            'member': member_handler,
            'device': device_handler,
            'room': room_handler,
            'switch': switch_handler,
            'port': port_handler,
            'account_type': account_type_handler,
            'payment_method': payment_method_handler,
            'account': account_handler,
            'product': product_handler,
            'bug_report': bug_report_handler,
            'treasury': treasury_handler,
            'vlan': vlan_handler
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
