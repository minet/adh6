from adh6.decorator import log_call
from adh6.default.crud_manager import CRUDManager
from adh6.entity.abstract_port import AbstractPort
from adh6.entity.port import Port
from adh6.exceptions import PortNotFoundError

from .interfaces.port_repository import PortRepository


class PortManager(CRUDManager):
    def __init__(self, port_repository: PortRepository):
        super().__init__(port_repository, PortNotFoundError)
        self.port_repository = port_repository

    @log_call
    async def create(self, body: AbstractPort) -> Port:
        """Create a new port."""
        return await self.port_repository.create(body)

    @log_call
    async def update(self, id: int, body: AbstractPort) -> None:
        """Update an existing port."""
        # Check if port exists
        port = await self.port_repository.get_by_id(id)
        if not port:
            raise PortNotFoundError(id)
        # Update port
        body.id = id
        await self.port_repository.update(body, override=True)
