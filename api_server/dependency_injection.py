import pinject
import abc

from src.plugins.treasury.interface_adapters.http import *
from src.plugins.member.interface_adapters.http import *
from src.plugins.device.interface_adapters.http import *
from src.interface_adapter.http_api.default import DefaultHandler
from src.interface_adapter.http_api.bug_report import BugReportHandler
from src.interface_adapter.http_api.health import HealthHandler
from src.interface_adapter.http_api.port import PortHandler
from src.interface_adapter.http_api.vlan import VLANHandler
from src.interface_adapter.http_api.product import ProductHandler
from src.interface_adapter.http_api.room import RoomHandler
from src.interface_adapter.http_api.switch import SwitchHandler

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
    BugReportHandler,
    TreasuryHandler,
    VLANHandler
]

from src.plugins.treasury.use_cases.account_manager import AccountManager
from src.plugins.treasury.use_cases.account_type_manager import AccountTypeManager
from src.plugins.treasury.use_cases.cashbox_manager import CashboxManager
from src.plugins.treasury.use_cases.payment_method_manager import PaymentMethodManager
from src.plugins.treasury.use_cases.transaction_manager import TransactionManager
from src.plugins.member.use_cases.member_manager import MemberManager
from src.plugins.device.use_cases.device_manager import DeviceManager
from src.use_case.bug_report_manager import BugReportManager
from src.use_case.crud_manager import CRUDManager
from src.use_case.health_manager import HealthManager
from src.use_case.port_manager import PortManager
from src.use_case.product_manager import ProductManager
from src.use_case.room_manager import RoomManager
from src.use_case.switch_manager import SwitchManager
from src.use_case.vlan_manager import VlanManager

managers = [
    DeviceManager,
    HealthManager,
    BugReportManager,
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
    VlanManager
]

from src.plugins.treasury.interface_adapters.storage import (
    TransactionSQLRepository, 
    AccountSQLRepository, 
    PaymentMethodSQLRepository, 
    AccountTypeSQLRepository, 
    CashboxSQLRepository
)
from src.plugins.member.interface_adapters.storage import (
    MembershipSQLRepository,
    MemberSQLRepository
)
from src.plugins.device.interface_adapters.storage import (
    DeviceSQLRepository,
    IPSQLAllocator
)
from src.interface_adapter.sql import repositories as sql_repositories
from src.interface_adapter.elasticsearch import ElasticSearchRepository
from src.interface_adapter.snmp import SwitchSNMPNetworkManager
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.crud_repository import CRUDRepository

def get_obj_graph():
    _global = sql_repositories+ \
        managers+ \
        handlers+ \
        [SwitchSNMPNetworkManager, ElasticSearchRepository]+ \
        [TransactionSQLRepository, AccountTypeSQLRepository, AccountSQLRepository, PaymentMethodSQLRepository, CashboxSQLRepository]+ \
        [MemberSQLRepository, MembershipSQLRepository] + \
        [DeviceSQLRepository, IPSQLAllocator]

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
