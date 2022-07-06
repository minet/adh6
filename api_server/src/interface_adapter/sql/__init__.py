# coding=utf-8
from .ping_repository import PingSQLRepository
from .product_repository import ProductSQLRepository
from .room_repository import RoomSQLRepository
from .switch_repository import SwitchSQLRepository
from .port_repository import PortSQLRepository
from .vlan_repository import VLANSQLRepository

repositories = [
    PingSQLRepository,
    ProductSQLRepository,
    RoomSQLRepository,
    SwitchSQLRepository,
    PortSQLRepository,
    VLANSQLRepository
]
