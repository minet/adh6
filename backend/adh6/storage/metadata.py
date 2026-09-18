"""Complete SQLAlchemy metadata used by Alembic and schema tooling."""

from adh6.authentication.storage import models as authentication_models  # noqa: F401
from adh6.device.storage import models as device_models  # noqa: F401
from adh6.member.storage import models as member_models  # noqa: F401
from adh6.mini_router.storage import models as mini_router_models  # noqa: F401
from adh6.network.storage import models as network_models  # noqa: F401
from adh6.room.storage import models as room_models  # noqa: F401
from adh6.storage.sql import models as legacy_models  # noqa: F401
from adh6.subnet.storage import models as subnet_models  # noqa: F401
from adh6.treasury.storage import models as treasury_models  # noqa: F401

from .base import Base

__all__ = ["Base"]
