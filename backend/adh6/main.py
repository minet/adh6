"""FastAPI application entry point for ADH6."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from adh6.authentication.middleware import authenticate
from adh6.authentication.oidc.token_verifier import close_oidc_token_verifier, get_oidc_token_verifier
from adh6.authentication.router import role_router, router as auth_router
from adh6.device.router import router as device_router
from adh6.exceptions import (
    AlreadyExistsError,
    IntMustBePositive,
    NetworkManagerReadError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from adh6.member.router import (
    charter_router,
    close_logs_repository,
    mailinglist_router,
    router as member_router,
)
from adh6.metrics.router import router as metrics_router
from adh6.mini_router.router import router as mini_router_router
from adh6.misc.router import router as misc_router
from adh6.naina.router import router as naina_router
from adh6.network.router import port_router, switch_router
from adh6.room.router import router as room_router
from adh6.subnet.router import router as subnet_router, vlans_router
from adh6.treasury.router import (
    payment_method_router,
    product_router,
    router as treasury_router,
    transaction_router,
)

# ============================================================================
# Exception Handlers
# ============================================================================


async def handle_not_found_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle NotFoundError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def handle_unauthorized_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle UnauthorizedError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


async def handle_int_must_be_positive_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle IntMustBePositive exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def handle_validation_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle RequestValidationError exceptions (convert 422 -> 400).

    FastAPI returns 422 for validation errors, but our legacy tests expect 400.
    This handler maintains backward compatibility with the Flask/Connexion API.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def handle_already_exists_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle AlreadyExistsError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def handle_adh6_validation_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle ADH6 ValidationError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def handle_network_manager_read_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle NetworkManagerReadError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": str(exc)},
    )


# ============================================================================
# Lifespan Events
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Built eagerly so a missing OIDC configuration fails at startup, not on the first request.
    # The signing keys themselves are downloaded lazily.
    get_oidc_token_verifier()
    try:
        yield
    finally:
        await close_logs_repository()
        await close_oidc_token_verifier()


# ============================================================================
# FastAPI Application
# ============================================================================


app = FastAPI(
    title="ADH6 API",
    description="MiNET's ADH6 Platform - User, Device, and Treasury Management",
    version="2.0.0",
    lifespan=lifespan,
    dependencies=[Depends(authenticate)],
)


# ============================================================================
# Register Exception Handlers
# ============================================================================


app.add_exception_handler(RequestValidationError, handle_validation_error)
app.add_exception_handler(ValidationError, handle_adh6_validation_error)
app.add_exception_handler(AlreadyExistsError, handle_already_exists_error)
app.add_exception_handler(NotFoundError, handle_not_found_error)
app.add_exception_handler(UnauthorizedError, handle_unauthorized_error)
app.add_exception_handler(IntMustBePositive, handle_int_must_be_positive_error)
app.add_exception_handler(NetworkManagerReadError, handle_network_manager_read_error)


# ============================================================================
# Include Routers
# ============================================================================


# Misc routers (profile, health, etc.)
app.include_router(misc_router, prefix="/api")

# Authentication routers
app.include_router(auth_router, prefix="/api")
app.include_router(role_router, prefix="/api")

# Domain routers
app.include_router(device_router, prefix="/api")
app.include_router(member_router, prefix="/api")
app.include_router(mailinglist_router, prefix="/api")
app.include_router(charter_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")
app.include_router(naina_router, prefix="/api")
app.include_router(port_router, prefix="/api")
app.include_router(switch_router, prefix="/api")
app.include_router(room_router, prefix="/api")
app.include_router(mini_router_router, prefix="/api")
app.include_router(subnet_router, prefix="/api")
app.include_router(vlans_router, prefix="/api")

# Treasury sub-routers (separate prefixes per spec.yaml)
app.include_router(payment_method_router, prefix="/api")
app.include_router(product_router, prefix="/api")
app.include_router(transaction_router, prefix="/api")
app.include_router(treasury_router, prefix="/api")


# ============================================================================
# Root Endpoint
# ============================================================================


@app.get("/", tags=["info"])
async def root():
    """ADH6 API root endpoint."""
    return {
        "name": "ADH6 API",
        "version": "2.0.0",
        "description": "MiNET's ADH6 Platform",
        "docs_url": "/docs",
    }


# ============================================================================
# Health Check (Simple)
# ============================================================================


@app.get("/ping", tags=["health"])
async def ping():
    """Simple ping endpoint for health checks."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "adh6.main:app",
        host="0.0.0.0",  # noqa: S104 # Listen on all interfaces for container compatibility
        port=8000,
        reload=True,
    )
