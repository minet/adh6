from adh6.decorator import log_call
from adh6.default.crud_manager import CRUDManager
from adh6.entity.abstract_port import AbstractPort
from adh6.entity.port import Port
from adh6.exceptions import NetworkManagerReadError, NotFoundError, PortNotFoundError, ValidationError

from .interfaces.port_repository import PortRepository
from .interfaces.switch_network_manager import BulkOperationData, DiscoveredPortData, SwitchNetworkManager
from .port_identity import normalize_port_oid


class PortManager(CRUDManager):
    def __init__(self, port_repository: PortRepository, network: SwitchNetworkManager | None = None) -> None:
        super().__init__(port_repository, PortNotFoundError)
        self.port_repository = port_repository
        self.network = network

    @log_call
    async def create(self, body: AbstractPort) -> Port:
        """Create a new port."""
        return await self.port_repository.create(self._validate_creation(await self._from_discovery(body, {})))

    @log_call
    async def bulk_create(self, bodies: list[AbstractPort]) -> BulkOperationData:
        """Bulk create ports."""
        success, failed, errors = 0, 0, []
        errors: list[str]
        cache: dict[int, list[DiscoveredPortData] | Exception] = {}
        for body in sorted(bodies, key=lambda port: port.switch_obj if port.switch_obj is not None else -1):
            try:
                await self.port_repository.create(self._validate_creation(await self._from_discovery(body, cache)))
                success += 1
            except Exception as e:
                failed += 1
                errors.append(f"Port {body.port_number} (OID {body.oid}): {e}")
        return {"success": success, "failed": failed, "errors": errors}

    @log_call
    async def update(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, id: int, body: AbstractPort
    ) -> None:
        """Update an existing port."""
        # Check if port exists
        port = await self.port_repository.get_by_id(id)
        if not port:
            raise PortNotFoundError(id)
        if (body.oid is not None and body.oid != port.oid) or (
            body.switch_obj is not None and body.switch_obj != port.switch_obj
        ):
            body = await self._from_discovery(
                body.model_copy(
                    update={
                        "oid": body.oid if body.oid is not None else port.oid,
                        "switch_obj": body.switch_obj if body.switch_obj is not None else port.switch_obj,
                    }
                ),
                {},
            )
        oid = body.oid if body.oid is not None else ""
        if oid != port.oid:
            body = body.model_copy(update={"oid": normalize_port_oid(oid)})
        # Update port
        body.id = id
        await self.port_repository.update(body, override=True)

    @log_call
    async def assign_room(self, id: int, room_id: int | None, expected_room: int | None) -> Port:
        return await self.port_repository.assign_room(id, room_id, expected_room)

    async def _from_discovery(
        self, body: AbstractPort, cache: dict[int, list[DiscoveredPortData] | Exception]
    ) -> AbstractPort:
        if self.network is None:
            return body
        oid = normalize_port_oid(body.oid)
        if body.switch_obj is None:
            raise ValidationError("A switch is required for a port")
        if body.switch_obj not in cache:
            try:
                cache[body.switch_obj] = await self.network.discover_ports(body.switch_obj)
            except (NotFoundError, NetworkManagerReadError) as e:
                cache[body.switch_obj] = e
        discovered = cache[body.switch_obj]
        if isinstance(discovered, Exception):
            raise discovered
        for port in discovered:
            if normalize_port_oid(port["oid"]) == oid:
                return body.model_copy(update={"oid": oid, "port_number": port["portNumber"]})
        raise ValidationError(f"Port {oid} was not found by SNMP discovery on switch {body.switch_obj}")

    @staticmethod
    def _validate_creation(body: AbstractPort) -> AbstractPort:
        if body.switch_obj is None:
            raise ValidationError("A switch is required for a port")
        oid = normalize_port_oid(body.oid)
        if not body.port_number or not body.port_number.strip():
            raise ValidationError("A port name is required")
        return body.model_copy(update={"oid": oid, "port_number": body.port_number.strip()})
