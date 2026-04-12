"""FastAPI router for member endpoints (members, charters, mailinglists, subscriptions)."""

import re
from datetime import datetime
from functools import lru_cache
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import Roles
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.database import get_session
from adh6.device import DeviceIpManager, DeviceLogsManager
from adh6.device.storage import (
    DeviceRepository as DeviceStorageRepository,
    IPAllocator,
    LogsRepository,
)
from adh6.entity import (
    Comment,
    Member,
    MemberBody,
    MemberFilter,
    MemberIdLogsGet200Response,
    Membership,
    MemberStatus,
    SubscriptionBody,
)
from adh6.exceptions import MemberAlreadyExist, NotFoundError
from adh6.security import require_role_or_ownership
from adh6.subnet.storage import VLANRepository
from adh6.subnet.vlan_manager import VlanManager
from adh6.treasury.storage import (
    AccountRepository,
    AccountTypeRepository,
    CashboxRepository,
    PaymentMethodRepository,
    TransactionRepository,
)
from adh6.treasury.transaction_manager import TransactionManager
from adh6.utils.filter_wrapper import MemberFilterWrapper

from .charter_manager import CharterManager
from .mailinglist_manager import MailinglistManager
from .member_manager import MemberManager
from .notification_manager import NotificationManager
from .smtp.notification_repository import NotificationSMTPRepository
from .storage import (
    CharterRepository,
    MailinglistReposiroty,
    MemberRepository,
    MembershipRepository,
)
from .storage.notification_template_repository import NotificationTemplateSQLRepository
from .subscription_manager import SubscriptionManager

router = APIRouter(prefix="/member", tags=["member"])
mailinglist_router = APIRouter(prefix="/mailinglist", tags=["mailinglist"])
charter_router = APIRouter(prefix="/charter", tags=["charter"])


def _is_valid_email(email: str | None) -> bool:
    if not email:
        return False
    # Keep validation intentionally lightweight and aligned with legacy expectations.
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is not None


def _member_to_response_dict(member: Member) -> dict[str, Any]:
    """Serialize generated OpenAPI entity with aliases expected by integration tests."""
    return member.model_dump(mode="json", by_alias=True, exclude_none=True)


def _apply_only_projection(payload: dict[str, Any], only: str | None) -> dict[str, Any]:
    """Apply legacy `only` behavior while always keeping `id`."""
    if not only:
        return payload

    # Valid fields from Member entity (using camelCase aliases)
    valid_fields = {
        "id",
        "username",
        "firstName",
        "lastName",
        "email",
        "comment",
        "departureDate",
        "mailinglist",
        "ip",
        "subnet",
        "membership",
    }

    wanted = {field.strip() for field in only.split(",") if field.strip()}
    wanted.add("id")

    # Check if any field is invalid
    invalid_fields = wanted - valid_fields
    if invalid_fields:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid field(s) in 'only' parameter: {', '.join(invalid_fields)}",
        )

    return {k: v for k, v in payload.items() if k in wanted}


@lru_cache(maxsize=1)
def get_logs_repository() -> LogsRepository:
    """Reuse Elasticsearch client wrapper across requests."""
    return LogsRepository()


@lru_cache(maxsize=1)
def get_notification_repository() -> NotificationSMTPRepository:
    """Reuse notification repository instance across requests."""
    return NotificationSMTPRepository()


def build_notification_manager(session: AsyncSession) -> NotificationManager:
    """Build notification manager for the current DB session."""
    return NotificationManager(
        notification_repository=get_notification_repository(),
        notification_template_repository=NotificationTemplateSQLRepository(session),
    )


def build_transaction_manager(session: AsyncSession) -> TransactionManager:
    """Build transaction manager for the current DB session."""
    return TransactionManager(
        transaction_repository=TransactionRepository(session),
        cashbox_repository=CashboxRepository(session),
    )


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_member_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MemberManager:
    """Dependency: Inject Member Manager."""
    member_repo = MemberRepository(session)
    account_repo = AccountRepository(session)
    account_type_repo = AccountTypeRepository(session)
    device_repo = DeviceStorageRepository(session)
    device_ip_manager = DeviceIpManager(
        ip_allocator=IPAllocator(session),
        device_repository=device_repo,
        vlan_manager=VlanManager(VLANRepository(session)),
    )

    device_logs_manager = DeviceLogsManager(
        device_repository=DeviceStorageRepository(session),
        logs_repository=get_logs_repository(),
    )

    notification_manager = build_notification_manager(session)
    transaction_manager = build_transaction_manager(session)
    subscription_manager = SubscriptionManager(
        member_repository=member_repo,
        membership_repository=MembershipRepository(session),
        charter_repository=CharterRepository(session),
        notification_manager=notification_manager,
        transaction_manager=transaction_manager,
        payment_method_repository=PaymentMethodRepository(session),
        account_repository=account_repo,
    )

    return MemberManager(
        member_repository=member_repo,
        account_repository=account_repo,
        account_type_repository=account_type_repo,
        device_ip_manager=device_ip_manager,
        device_logs_manager=device_logs_manager,
        mailinglist_repository=MailinglistReposiroty(session),
        subscription_manager=subscription_manager,
    )


async def get_charter_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CharterManager:
    """Dependency: Inject Charter Manager."""
    charter_repo = CharterRepository(session)
    member_repo = MemberRepository(session)
    membership_repo = MembershipRepository(session)
    return CharterManager(charter_repo, member_repo, membership_repo)


async def get_mailinglist_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MailinglistManager:
    """Dependency: Inject Mailinglist Manager."""
    member_repo = MemberRepository(session)
    mailinglist_repo = MailinglistReposiroty(session)
    return MailinglistManager(member_repo, mailinglist_repo)


async def get_subscription_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SubscriptionManager:
    """Dependency: Inject Subscription Manager."""
    member_repo = MemberRepository(session)
    notification_manager = build_notification_manager(session)
    transaction_manager = build_transaction_manager(session)
    return SubscriptionManager(
        member_repository=member_repo,
        membership_repository=MembershipRepository(session),
        charter_repository=CharterRepository(session),
        notification_manager=notification_manager,
        transaction_manager=transaction_manager,
        payment_method_repository=PaymentMethodRepository(session),
        account_repository=AccountRepository(session),
    )


# ============================================================================
# Member Endpoints
# ============================================================================


@router.post("", response_model=int, status_code=status.HTTP_201_CREATED)
async def create_member(
    body: MemberBody,
    manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
) -> int:
    """Create a new member."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value)
    if not _is_valid_email(body.mail):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )
    try:
        member = await manager.create(body)
    except MemberAlreadyExist as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return member.id


@router.get("", response_model=list[int])
async def search_members(
    manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
    response: Response,
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str, Query()] = "",
    filter_: Annotated[MemberFilter, MemberFilterWrapper()] = MemberFilter(),
) -> list[int]:
    """Search members with optional filter."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    result, _count = await manager.search(limit=limit, offset=offset, terms=terms, filter_=filter_)
    response.headers["X-Total-Count"] = str(_count)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    # result = [await manager.get_by_id(member_id) for member_id in result]
    return result


@router.get("/{id}", response_model=Member)
async def get_member(
    id: int,
    manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
    only: Annotated[str | None, Query()] = None,
) -> Any:
    """Get a specific member by ID."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value, id, "member")
    try:
        result = await manager.get_by_id(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if only:
        return JSONResponse(content=_apply_only_projection(_member_to_response_dict(result), only))
    return result


@router.patch("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_member(
    id: int,
    body: MemberBody,
    manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
) -> None:
    """Update a member."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value, id, "member")
    try:
        await manager.update(id, body)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    id: int,
    manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
) -> None:
    """Delete a member."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value, id, "member")
    try:
        await manager.delete(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{id}/comment", response_model=Comment)
async def get_member_comment(
    id: int,
    manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
) -> Comment:
    """Get comment for a member."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value, id, "member comment")
    try:
        return await manager.get_comment(id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{id}/comment", status_code=status.HTTP_204_NO_CONTENT)
async def set_member_comment(
    id: int,
    body: Comment,
    manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
) -> None:
    """Set comment for a member."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value)
    await manager.change_comment(id, body)


# ============================================================================
# Subscription Endpoints
# ============================================================================


@router.post("/{id}/subscription", status_code=status.HTTP_200_OK, response_model=Membership)
async def create_subscription(
    id: int,
    body: SubscriptionBody,
    manager: Annotated[SubscriptionManager, Depends(get_subscription_manager)],
    request: Request,
) -> Membership:
    """Add a membership record for a member."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value, id, "subscription")
    membership = await manager.create(id, body)
    return membership


# ============================================================================
# Member Logs, Password, and Statuses Endpoints
# ============================================================================


@router.get("/{id}/logs", response_model=MemberIdLogsGet200Response)
async def get_member_logs(
    id: int,
    manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
    dhcp: Annotated[bool, Query()] = False,
    limit: Annotated[int, Query(ge=0)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    """Get logs for a member."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value, id, "member logs")
    try:
        return await manager.get_logs(id, limit=limit, offset=offset, dhcp=dhcp)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{id}/password", status_code=status.HTTP_204_NO_CONTENT)
async def set_member_password(
    id: int,
    body: dict,
    manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
) -> None:
    """Set the password of a member."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value, id, "password")
    try:
        password = body.get("password")
        hashed_password = body.get("hashedPassword")
        await manager.change_password(id, password or "", hashed_password)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{id}/statuses", response_model=list[MemberStatus])
async def get_member_statuses(
    id: int,
    manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
) -> list[MemberStatus]:
    """Get statuses for a member."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value, id, "member")
    try:
        return await manager.get_statuses(id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ============================================================================
# Subscription Management Endpoints
# ============================================================================


@router.patch("/{id}/subscription", status_code=status.HTTP_204_NO_CONTENT)
async def update_subscription(
    id: int,
    body: SubscriptionBody,
    manager: Annotated[SubscriptionManager, Depends(get_subscription_manager)],
    request: Request,
) -> None:
    """Update a member's subscription."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value, id, "subscription")
    await manager.update(id, body)


@router.post("/{id}/subscription/validate", status_code=status.HTTP_204_NO_CONTENT)
async def validate_subscription(
    id: int,
    subscription_manager: Annotated[SubscriptionManager, Depends(get_subscription_manager)],
    member_manager: Annotated[MemberManager, Depends(get_member_manager)],
    request: Request,
    free: Annotated[bool, Query()] = False,
) -> None:
    """Validate a member's subscription."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value)
    await subscription_manager.validate(id, free)
    await member_manager.update_subnet(id)


# ============================================================================
# Charter Specific Endpoints
# ============================================================================


@router.get("/{id}/charter/{charter_id}", response_model=str)
async def get_member_charter_by_id(
    id: int,
    charter_id: int,
    manager: Annotated[CharterManager, Depends(get_charter_manager)],
    request: Request,
) -> str:
    """Get a specific charter for a member."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value, id, "charter")
    try:
        signed_at = await manager.get(charter_id=charter_id, member_id=id)
        if isinstance(signed_at, datetime):
            return signed_at.isoformat()
        return "" if signed_at is None else str(signed_at)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{id}/charter/{charter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def sign_specific_charter(
    id: int,
    charter_id: int,
    manager: Annotated[CharterManager, Depends(get_charter_manager)],
    request: Request,
) -> None:
    """Sign a specific charter for a member."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value, id, "charter")
    try:
        await manager.sign(charter_id=charter_id, member_id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ============================================================================
# Root Mailinglist Endpoints
# ============================================================================


@mailinglist_router.get("", response_model=list[int])
async def search_mailinglist_members(
    value: Annotated[int, Query(ge=0, le=255)],
    manager: Annotated[MailinglistManager, Depends(get_mailinglist_manager)],
    request: Request,
) -> list[int]:
    """Retrieve members subscribed to a specific mailing list value."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    result = await manager.get_members(value)
    return list(result)


@mailinglist_router.get("/member/{id}", response_model=int)
async def get_mailinglist_member_value(
    id: int,
    manager: Annotated[MailinglistManager, Depends(get_mailinglist_manager)],
    request: Request,
) -> int:
    """Retrieve mailing list membership value for one member."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value, owner_id=id)
    return await manager.get_member_mailinglist(id)


@mailinglist_router.put("/member/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_mailinglist_member_value(
    id: int,
    body: dict,
    manager: Annotated[MailinglistManager, Depends(get_mailinglist_manager)],
    request: Request,
) -> None:
    """Update mailing list membership value for one member."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value, owner_id=id)
    await manager.update_member_mailinglist(id, int(body.get("value", 0)))


# ============================================================================
# Root Charter Endpoints
# ============================================================================


@charter_router.get("/{charter_id}/member", response_model=list[int])
async def list_charter_members(
    charter_id: int,
    manager: Annotated[CharterManager, Depends(get_charter_manager)],
    request: Request,
    response: Response,
) -> list[int]:
    """List members who signed a charter."""
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    result, _count = await manager.get_members(charter_id)
    response.headers["X-Total-Count"] = str(_count)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    return list(result)


@charter_router.get("/{charter_id}/member/{id}", response_model=str | None)
async def get_member_charter_signature(
    charter_id: int,
    id: int,
    manager: Annotated[CharterManager, Depends(get_charter_manager)],
    request: Request,
) -> str | None:
    """Get signature date for a charter and member."""
    require_role_or_ownership(request, Roles.USER.value, id, "charter")
    signed_at = await manager.get(charter_id, id)
    if isinstance(signed_at, datetime):
        return signed_at.isoformat()
    return "" if signed_at is None else str(signed_at)


@charter_router.post(
    "/{charter_id}/member/{id}",
    status_code=status.HTTP_201_CREATED,
    response_class=Response,
)
async def sign_member_charter(
    charter_id: int,
    id: int,
    manager: Annotated[CharterManager, Depends(get_charter_manager)],
    request: Request,
) -> Response:
    """Sign a charter for a member."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value, id, "charter")
    await manager.sign(charter_id, id)
    return Response(status_code=status.HTTP_201_CREATED)


__all__ = ["charter_router", "mailinglist_router", "router"]
