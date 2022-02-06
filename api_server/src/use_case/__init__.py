# coding=utf-8
from .account_manager import AccountManager
from .account_type_manager import AccountTypeManager
from .bug_report_manager import BugReportManager
from .cashbox_manager import CashboxManager
from .crud_manager import CRUDManager
from .device_manager import DeviceManager
from .health_manager import HealthManager
from .member_manager import MemberManager
from .payment_method_manager import PaymentMethodManager
from .port_manager import PortManager
from .product_manager import ProductManager
from .room_manager import RoomManager
from .stats_manager import StatsManager
from .switch_manager import SwitchManager
from .transaction_manager import TransactionManager
from .vlan_manager import VlanManager

managers = [
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
    VlanManager
]