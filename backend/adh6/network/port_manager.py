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
    async def bulk_create(self, bodies: list[AbstractPort]) -> dict:
        """Bulk create ports."""
        success, failed, errors = 0, 0, []
        for body in bodies:
            try:
                await self.port_repository.create(body)
                success += 1
            except Exception as e:
                failed += 1
                errors.append(f"Port {body.port_number} (OID {body.oid}): {e}")
        return {"success": success, "failed": failed, "errors": errors}

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
