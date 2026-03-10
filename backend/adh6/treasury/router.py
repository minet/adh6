"""FastAPI router for treasury endpoints (accounts, transactions, products, etc.)."""

import json
from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import Roles
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.database import get_session
from adh6.entity import (
    AbstractAccount,
    AbstractTransaction,
    Account,
    AccountType,
    Bank,
    Cashbox,
    PaymentMethod,
    Product,
    Transaction,
)
from adh6.exceptions import NotFoundError
from adh6.security import require_role_or_ownership

from .account_manager import AccountManager
from .account_type_manager import AccountTypeManager
from .cashbox_manager import CashboxManager
from .payment_method_manager import PaymentMethodManager
from .product_manager import ProductManager
from .storage import (
    AccountRepository,
    AccountTypeRepository,
    CashboxRepository,
    PaymentMethodRepository,
    ProductRepository,
    TransactionRepository,
)
from .transaction_manager import TransactionManager

# Create separate routers for each domain (as per spec.yaml)
router = APIRouter(prefix="/treasury", tags=["treasury"])
account_router = APIRouter(prefix="/account", tags=["account"])
account_type_router = APIRouter(prefix="/account_type", tags=["account_type"])
payment_method_router = APIRouter(prefix="/payment_method", tags=["payment_method"])
product_router = APIRouter(prefix="/product", tags=["product"])
transaction_router = APIRouter(prefix="/transaction", tags=["transaction"])


def _extract_filter_entries(request: Request) -> dict[str, str]:
    """Extract deepObject query params formatted as filter[field]=value."""
    filters: dict[str, str] = {}
    for raw_key, raw_value in request.query_params.multi_items():
        if not raw_key.startswith("filter[") or not raw_key.endswith("]"):
            continue

        key = raw_key[len("filter[") : -1]
        if key:
            filters[key] = raw_value
    return filters


def _parse_account_filter(request: Request, raw_filter: str | None) -> AbstractAccount | None:
    """Parse account filter from either JSON string or deepObject query params."""
    if raw_filter:
        return AbstractAccount.from_dict(json.loads(raw_filter))

    raw = _extract_filter_entries(request)
    if not raw:
        return None

    payload: dict[str, object] = {}
    if "id" in raw and raw["id"] != "":
        payload["id"] = int(raw["id"])
    if "name" in raw:
        payload["name"] = raw["name"]
    if "member" in raw and raw["member"] != "":
        payload["member"] = int(raw["member"])
    if "accountType" in raw and raw["accountType"] != "":
        payload["accountType"] = int(raw["accountType"])
    if "actif" in raw:
        payload["actif"] = raw["actif"].lower() == "true"
    if "pinned" in raw:
        payload["pinned"] = raw["pinned"].lower() == "true"
    if "compteCourant" in raw:
        payload["compteCourant"] = raw["compteCourant"].lower() == "true"

    return AbstractAccount.from_dict(payload)


def _parse_transaction_filter(request: Request, raw_filter: str | None) -> AbstractTransaction | None:
    """Parse transaction filter from either JSON string or deepObject query params."""
    if raw_filter:
        return AbstractTransaction.from_dict(json.loads(raw_filter))

    raw = _extract_filter_entries(request)
    if not raw:
        return None

    payload: dict[str, object] = {}
    if "id" in raw and raw["id"] != "":
        payload["id"] = int(raw["id"])
    if "name" in raw:
        payload["name"] = raw["name"]
    if "src" in raw and raw["src"] != "":
        payload["src"] = int(raw["src"])
    if "dst" in raw and raw["dst"] != "":
        payload["dst"] = int(raw["dst"])
    if "paymentMethod" in raw and raw["paymentMethod"] != "":
        payload["paymentMethod"] = int(raw["paymentMethod"])
    if "pendingValidation" in raw:
        payload["pendingValidation"] = raw["pendingValidation"].lower() == "true"

    return AbstractTransaction.from_dict(payload)


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_account_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AccountManager:
    """Dependency: Inject Account Manager."""
    repo = AccountRepository(session)
    return AccountManager(repo)


async def get_account_type_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AccountTypeManager:
    """Dependency: Inject Account Type Manager."""
    repo = AccountTypeRepository(session)
    return AccountTypeManager(repo)


async def get_cashbox_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CashboxManager:
    """Dependency: Inject Cashbox Manager."""
    repo = CashboxRepository(session)
    return CashboxManager(repo)


async def get_payment_method_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PaymentMethodManager:
    """Dependency: Inject Payment Method Manager."""
    repo = PaymentMethodRepository(session)
    return PaymentMethodManager(repo)


async def get_transaction_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TransactionManager:
    """Dependency: Inject Transaction Manager."""
    repo = TransactionRepository(session)
    return TransactionManager(repo, CashboxRepository(session))


async def get_product_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
    transaction_manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
) -> ProductManager:
    """Dependency: Inject Product Manager."""
    product_repo = ProductRepository(session)
    return ProductManager(
        product_repository=product_repo,
        transaction_manager=transaction_manager,
        payment_method_repository=PaymentMethodRepository(session),
        account_repository=AccountRepository(session),
    )


# ============================================================================
# Account Endpoints
# ============================================================================


@account_router.get("", response_model=list[Account])
async def search_accounts(
    manager: Annotated[AccountManager, Depends(get_account_manager)],
    request: Request,
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
    filter_: Annotated[str | None, Query()] = None,
) -> list[Account]:
    """Search accounts."""
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    filter_obj = _parse_account_filter(request, filter_)
    result, _count = await manager.search(
        limit=limit,
        offset=offset,
        terms=terms,
        filter_=filter_obj,
    )
    return result


@account_router.post("", response_model=Account, status_code=status.HTTP_200_OK)
async def create_account(
    body: Account,
    manager: Annotated[AccountManager, Depends(get_account_manager)],
    request: Request,
) -> Account:
    """Create an account."""
    require_role_or_ownership(request, Roles.TRESO_WRITE.value)
    account, _created = await manager.update_or_create(obj=body)
    return account


@account_router.get("/{id}", response_model=Account)
async def get_account(
    id: int,
    manager: Annotated[AccountManager, Depends(get_account_manager)],
    request: Request,
) -> Account:
    """Get a specific account."""
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    try:
        return await manager.get_by_id(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@account_router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_account(
    id: int,
    body: Account,
    manager: Annotated[AccountManager, Depends(get_account_manager)],
    request: Request,
) -> None:
    """Update an account."""
    require_role_or_ownership(request, Roles.TRESO_WRITE.value)
    await manager.update_or_create(obj=body, id=id)


# ============================================================================
# Account Type Endpoints
# ============================================================================


@account_type_router.get("", response_model=list[AccountType])
async def search_account_types(
    manager: Annotated[AccountTypeManager, Depends(get_account_type_manager)],
    request: Request,
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
) -> list[AccountType]:
    """Search account types."""
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    result, _count = await manager.search(limit=limit, offset=offset, terms=terms)
    return result


@account_type_router.get("/{id}", response_model=AccountType)
async def get_account_type(
    id: int,
    manager: Annotated[AccountTypeManager, Depends(get_account_type_manager)],
    request: Request,
) -> AccountType:
    """Get a specific account type."""
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    try:
        return await manager.get_by_id(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ============================================================================
# Payment Method Endpoints
# ============================================================================


@payment_method_router.get("", response_model=list[PaymentMethod])
async def search_payment_methods(
    manager: Annotated[PaymentMethodManager, Depends(get_payment_method_manager)],
    request: Request,
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
) -> list[PaymentMethod]:
    """Search payment methods."""
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    result, _count = await manager.search(limit=limit, offset=offset, terms=terms)
    return result


@payment_method_router.get("/{id}", response_model=PaymentMethod)
async def get_payment_method(
    id: int,
    manager: Annotated[PaymentMethodManager, Depends(get_payment_method_manager)],
    request: Request,
) -> PaymentMethod:
    """Get a specific payment method."""
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    try:
        return await manager.get_by_id(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ============================================================================
# Product Endpoints
# ============================================================================


@product_router.get("", response_model=list[Product])
async def search_products(
    manager: Annotated[ProductManager, Depends(get_product_manager)],
    request: Request,
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
) -> list[Product]:
    """Search products."""
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    result, _count = await manager.search(limit=limit, offset=offset, terms=terms)
    return result


@product_router.get("/{id}", response_model=Product)
async def get_product(
    id: int,
    manager: Annotated[ProductManager, Depends(get_product_manager)],
    request: Request,
) -> Product:
    """Get a specific product."""
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    try:
        return await manager.get_by_id(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@product_router.post("/buy", status_code=status.HTTP_204_NO_CONTENT)
async def buy_product(
    member_id: Annotated[int, Query(alias="memberId")],
    payment_method: Annotated[int, Query(alias="paymentMethod")],
    products: Annotated[list[int], Query()],
    manager: Annotated[ProductManager, Depends(get_product_manager)],
    request: Request,
) -> None:
    """Buy products."""
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value)
    await manager.buy(
        member_id=member_id,
        payment_method_id=payment_method,
        product_ids=products,
    )


# ============================================================================
# Transaction Endpoints
# ============================================================================


@transaction_router.get("")
async def search_transactions(
    manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
    request: Request,
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
    filter_: Annotated[str | None, Query()] = None,
    only: Annotated[str | None, Query()] = None,
) -> list[Transaction] | list[dict]:
    """Search transactions."""
    require_role_or_ownership(request, Roles.TRESO_READ.value)
    filter_obj = _parse_transaction_filter(request, filter_)
    result, _count = await manager.search(
        limit=limit,
        offset=offset,
        terms=terms,
        filter_=filter_obj,
    )

    if only:
        # Validate only fields are valid
        valid_fields = {
            "id",
            "name",
            "src",
            "dst",
            "timestamp",
            "paymentMethod",
            "value",
            "attachments",
            "author",
            "pendingValidation",
            "cashbox",
        }
        requested_fields = set(only.split(","))
        invalid_fields = requested_fields - valid_fields
        if invalid_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid fields: {', '.join(invalid_fields)}",
            )

        only_fields = {"id", *requested_fields}
        result = [{k: v for k, v in item.model_dump(by_alias=True).items() if k in only_fields} for item in result]

    return result


@transaction_router.post("", response_model=Transaction, status_code=status.HTTP_200_OK)
async def create_transaction(
    body: Transaction,
    manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
    request: Request,
) -> Transaction:
    """Create a transaction."""
    require_role_or_ownership(request, Roles.TRESO_WRITE.value)
    abstract = AbstractTransaction.from_dict(body.to_dict())
    if abstract is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid transaction data")
    transaction, _created = await manager.update_or_create(abstract)
    return transaction


@transaction_router.get("/{id}", response_model=Transaction)
async def get_transaction(
    id: int,
    manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
    request: Request,
) -> Transaction:
    """Get a specific transaction."""
    require_role_or_ownership(request, Roles.TRESO_READ.value)
    try:
        return await manager.get_by_id(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@transaction_router.patch("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def patch_transaction(
    id: int,
    body: AbstractTransaction,
    manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
    request: Request,
) -> None:
    """Partially update a transaction."""
    require_role_or_ownership(request, Roles.TRESO_WRITE.value)
    await manager.partially_update(abstract_transaction=body, id=id)


@transaction_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    id: int,
    manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
    request: Request,
) -> None:
    """Delete a transaction."""
    require_role_or_ownership(request, Roles.TRESO_WRITE.value)
    await manager.delete(id=id)


@transaction_router.post("/{id}/upload", status_code=status.HTTP_204_NO_CONTENT)
async def upload_transaction_proof(
    id: int,
    body: Annotated[bytes, Body(media_type="application/octet-stream")],
    manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
    request: Request,
) -> None:
    """Upload proof for a transaction."""
    require_role_or_ownership(request, Roles.TRESO_WRITE.value)
    # TODO: Store binary proof for transaction attachments.
    _ = (id, body, manager)
    return None


@transaction_router.get("/{id}/validate", status_code=status.HTTP_204_NO_CONTENT)
async def validate_transaction(
    id: int,
    manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
    request: Request,
) -> Response:
    """Validate a transaction."""
    require_role_or_ownership(request, Roles.TRESO_READ.value)
    await manager.validate(id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============================================================================
# Treasury Endpoints (Cashbox & Bank)
# ============================================================================


@router.get("/cashbox", response_model=Cashbox)
async def get_cashbox(
    manager: Annotated[CashboxManager, Depends(get_cashbox_manager)],
    request: Request,
) -> Cashbox:
    """Get cashbox balance."""
    require_role_or_ownership(request, Roles.TRESO_READ.value)
    fond, coffre = await manager.get_cashbox()
    return Cashbox(fond=fond, coffre=coffre)


@router.get("/bank", response_model=Bank)
async def get_bank(
    manager: Annotated[AccountManager, Depends(get_account_manager)],
    request: Request,
) -> Bank:
    """Get bank account balance."""
    require_role_or_ownership(request, Roles.TRESO_READ.value)
    result = await manager.get_cav_balance()
    return Bank(expectedCav=result)
