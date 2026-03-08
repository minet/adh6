"""FastAPI router for metrics endpoints (health checks)."""

import json

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import Roles
from adh6.database import get_session
from adh6.security import require_role_or_ownership

from .health_manager import HealthManager
from .storage import PingRepository

router = APIRouter(prefix="/health", tags=["health"])


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_health_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> HealthManager:
    """Dependency: Inject Health Manager."""
    repo = PingRepository(session)
    return HealthManager(repo)


# ============================================================================
# Health Check Endpoints
# ============================================================================


@router.get("", status_code=status.HTTP_200_OK, response_class=Response)
async def health_check(
    manager: Annotated[HealthManager, Depends(get_health_manager)],
    request: Request,
) -> Response:
    """Perform a system health check."""
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    is_healthy = await manager.is_healthy()
    payload = {"healthy": is_healthy}
    return Response(
        content=json.dumps(payload),
        media_type="application/json",
        status_code=status.HTTP_200_OK,
    )
