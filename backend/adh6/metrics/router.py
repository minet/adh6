"""FastAPI router for metrics endpoints (health checks)."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.database import get_session
from adh6.entity import Health

from .health_manager import HealthCache, HealthManager
from .storage import PingRepository

router = APIRouter(prefix="/health", tags=["health"])

_health_cache = HealthCache()


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


@router.get(
    "",
    response_model=Health,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": Health}},
)
async def health_check(
    manager: Annotated[HealthManager, Depends(get_health_manager)],
) -> JSONResponse:
    """Readiness check: 200 when dependencies are ready, 503 otherwise."""
    is_healthy = await _health_cache.is_healthy(manager)
    return JSONResponse(
        content={"healthy": is_healthy},
        status_code=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        headers={"Cache-Control": "no-store"},
    )
