# coding=utf-8
from src.entity import Port, AbstractPort
from src.use_case.interface.crud_repository import CRUDRepository


class PortRepository(CRUDRepository[Port, AbstractPort]):
    pass
