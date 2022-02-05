import pinject
import abc

from src.interface_adapter.http_api.default import DefaultHandler

from src.interface_adapter.http_api import handlers

from src.interface_adapter.snmp.switch_network_manager import SwitchSNMPNetworkManager

from src.interface_adapter.elasticsearch.repository import ElasticSearchRepository

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
from src.use_case.crud_manager import CRUDManager
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
from src.use_case.interface.crud_repository import CRUDRepository

_repositories = [
    AccountSQLRepository,
    AccountTypeSQLRepository,
    CashboxSQLRepository,
    DeviceSQLRepository,
    IPSQLAllocator,
    MemberSQLRepository,
    MembershipSQLRepository,
    PaymentMethodSQLRepository,
    PingSQLRepository,
    PortSQLRepository,
    ProductSQLRepository,
    RoomSQLRepository,
    SwitchSQLRepository,
    TransactionSQLRepository,
    ElasticSearchRepository
]

_managers = [
    DeviceManager,
    HealthManager,
    StatsManager,
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
    SwitchSNMPNetworkManager,
]

class BindingSpec(pinject.BindingSpec):
    def __init__(self, configuration, testing) -> None:
        super().__init__()
        self.configration = configuration
        self.testing = testing
    def configure(self, bind):
        bind('configuration', to_instance=self.configration)
        bind('gitlab_conf', to_instance=self.configration.GITLAB_CONF)
        bind('testing', to_instance=self.testing)
        bind('ip_allocator', to_class=IPSQLAllocator)
        bind('vlan_manager', to_class=VLANManager)
        bind('vlan_repository', to_class=VLANSQLRepository)



_global = _repositories+_managers+handlers

def get_base_class(cls):
    if len(cls.__bases__) == 0 or cls.__bases__[0] == abc.ABC  or cls.__bases__[0] == object or cls.__bases__[0] == abc.ABC or cls.__bases__[0] == CRUDRepository or cls.__bases__[0] == CRUDManager or cls.__bases__[0] == DefaultHandler:
        return cls
    return get_base_class(cls.__bases__[0])

_class_name_to_abstract = {
    cls.__name__: get_base_class(cls) for cls in _global
}

def get_arg_names(class_name):
    if class_name in _class_name_to_abstract:
        class_name = _class_name_to_abstract[class_name].__name__
    return pinject.bindings.default_get_arg_names_from_class_name(class_name)

def get_obj_graph(configuration, testing):
    return pinject.new_object_graph(
        modules=None,
        binding_specs=[BindingSpec(configuration, testing)],
        classes=_global,
        get_arg_names_from_class_name=get_arg_names
    )