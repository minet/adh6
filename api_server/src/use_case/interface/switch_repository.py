# coding=utf-8
from src.entity import Switch, AbstractSwitch
from src.use_case.interface.crud_repository import CRUDRepository


class SwitchRepository(CRUDRepository[Switch, AbstractSwitch]):
    pass
