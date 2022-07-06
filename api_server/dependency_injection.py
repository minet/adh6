import pinject
import abc

from src.plugins.treasury.interface_adapters.http import *
from src.plugins.member.interface_adapters.http import *
from src.plugins.device.interface_adapters.http import *
from src.default.http_handler import DefaultHandler
from src.plugins.metrics.interface_adapters.http.health import HealthHandler
from src.plugins.network.interface_adapters.http.port import PortHandler
from src.plugins.subnet.interface_adapters.http.vlan import VLANHandler
from src.plugins.room.interface_adapters.http.room import RoomHandler
from src.plugins.network.interface_adapters.http.switch import SwitchHandler

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
    VLANHandler
]

from src.plugins.treasury.use_cases.account_manager import AccountManager
from src.plugins.treasury.use_cases.account_type_manager import AccountTypeManager
from src.plugins.treasury.use_cases.cashbox_manager import CashboxManager
from src.plugins.treasury.use_cases.payment_method_manager import PaymentMethodManager
from src.plugins.treasury.use_cases.transaction_manager import TransactionManager
from src.plugins.treasury.use_cases.product_manager import ProductManager
from src.plugins.member.use_cases.member_manager import MemberManager
from src.plugins.device.use_cases.device_manager import DeviceManager
from src.default.crud_manager import CRUDManager
from src.plugins.metrics.use_cases.health_manager import HealthManager
from src.plugins.network.use_cases.port_manager import PortManager
from src.plugins.room.use_cases.room_manager import RoomManager
from src.plugins.network.use_cases.switch_manager import SwitchManager
from src.plugins.subnet.use_cases.vlan_manager import VlanManager

managers = [
    DeviceManager,
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
from src.interface_adapter.elasticsearch import ElasticSearchRepository
from src.plugins.network.interface_adapters.snmp import SwitchSNMPNetworkManager
from src.default.crud_repository import CRUDRepository

def get_obj_graph():
    _global = managers+ \
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
