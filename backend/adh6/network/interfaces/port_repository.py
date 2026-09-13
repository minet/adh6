from adh6.default.crud_repository import CRUDRepository
from adh6.entity import AbstractPort, Port


class PortRepository(CRUDRepository[Port, AbstractPort]):
    pass
