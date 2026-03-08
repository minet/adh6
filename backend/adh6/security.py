"""Security and authorization utilities."""

from typing import Any

from fastapi import HTTPException, Request, status

from adh6.authentication.enums import Roles


# ============================================================================
# Token Info Extraction
# ============================================================================


def get_token_info(request: Request) -> dict[str, Any]:
    """Get token info from request state."""
    return getattr(request.state, "token_info", {})


def get_user_id(request: Request) -> int | None:
    """Get authenticated user ID from request."""
    token_info = get_token_info(request)
    return token_info.get("uid")


def get_user_roles(request: Request) -> list[str]:
    """Get user roles/scope from request."""
    token_info = get_token_info(request)
    return token_info.get("scope", [])


# ============================================================================
# Authorization Checks
# ============================================================================


def require_role_or_ownership(
    request: Request,
    role: str,
    owner_id: int | None = None,
    resource_name: str = "resource",
) -> None:
    """
    Check that user has the required role or owns the resource.

    Raises HTTPException (403 Forbidden) if user lacks both role and ownership.

    Args:
        request: FastAPI request object
        role: Required role name (e.g., "admin:write", "network:read")
        owner_id: ID of resource owner (optional)
        resource_name: Name of resource for error message
    """
    user_roles = get_user_roles(request)
    has_role = role in user_roles

    if has_role:
        return

    # If no role match, check ownership
    if owner_id is not None:
        user_id = get_user_id(request)
        if user_id is not None and user_id == owner_id:
            return

    # Determine error code: API key auth with wrong scope → 401, OIDC → 403
    token_info = get_token_info(request)
    if token_info.get("auth_method") == "api_key":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"API key lacks required scope to access this {resource_name}",
        )

    # User has neither role nor ownership
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Insufficient permissions to access this {resource_name}",
    )
