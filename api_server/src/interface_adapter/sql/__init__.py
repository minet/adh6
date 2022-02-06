# coding=utf-8
from .account_repository import AccountSQLRepository
from .account_type_repository import AccountTypeSQLRepository
from .cashbox_repository import CashboxSQLRepository
from .device_repository import DeviceSQLRepository
from .ip_allocator import IPSQLAllocator
from .member_repository import MemberSQLRepository
from .membership_repository import MembershipSQLRepository
from .money_repository import MoneySQLRepository
from .payment_method_repository import PaymentMethodSQLRepository
from .ping_repository import PingSQLRepository
from .product_repository import ProductSQLRepository
from .room_repository import RoomSQLRepository
from .switch_repository import SwitchSQLRepository
from .transaction_repository import TransactionSQLRepository
from .port_repository import PortSQLRepository
from .vlan_repository import VLANSQLRepository

repositories = [
    AccountSQLRepository,
    AccountTypeSQLRepository,
    CashboxSQLRepository,
    DeviceSQLRepository,
    IPSQLAllocator,
    MemberSQLRepository,
    MembershipSQLRepository,
    PaymentMethodSQLRepository,
    PingSQLRepository,
    ProductSQLRepository,
    RoomSQLRepository,
    SwitchSQLRepository,
    TransactionSQLRepository,
    MoneySQLRepository,
    PortSQLRepository
]