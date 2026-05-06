"""FastAPI router for treasury endpoints (transactions, products, payment methods, export)."""

import json
from datetime import date
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
from adh6.entity import (
    AbstractProduct,
    AbstractTransaction,
    PaymentMethod,
    Product,
    Transaction,
)
from adh6.exceptions import NotFoundError
from adh6.member.storage import MemberRepository, MembershipRepository
from adh6.security import get_user_id, require_role_or_ownership

from .export_manager import ExportManager
from .payment_method_manager import PaymentMethodManager
from .product_manager import ProductManager
from .storage import (
    PaymentMethodRepository,
    ProductRepository,
    TransactionRepository,
)
from .transaction_manager import TransactionManager

router = APIRouter(prefix="/treasury", tags=["treasury"])
payment_method_router = APIRouter(prefix="/payment_method", tags=["payment_method"])
product_router = APIRouter(prefix="/product", tags=["product"])
transaction_router = APIRouter(prefix="/transaction", tags=["transaction"])


def _extract_filter_entries(request: Request) -> dict[str, str]:
    filters: dict[str, str] = {}
    for raw_key, raw_value in request.query_params.multi_items():
        if not raw_key.startswith("filter[") or not raw_key.endswith("]"):
            continue
        key = raw_key[len("filter[") : -1]
        if key:
            filters[key] = raw_value
    return filters


def _parse_transaction_filter(request: Request, raw_filter: str | None) -> AbstractTransaction | None:
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
    if "paymentMethod" in raw and raw["paymentMethod"] != "":
        payload["paymentMethod"] = int(raw["paymentMethod"])
    if "productType" in raw:
        payload["productType"] = raw["productType"]
    if "membershipUuid" in raw:
        payload["membershipUuid"] = raw["membershipUuid"]

    return AbstractTransaction.from_dict(payload)


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_payment_method_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PaymentMethodManager:
    repo = PaymentMethodRepository(session)
    return PaymentMethodManager(repo)


async def get_transaction_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TransactionManager:
    repo = TransactionRepository(session)
    return TransactionManager(repo)


async def get_product_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
    transaction_manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
) -> ProductManager:
    product_repo = ProductRepository(session)
    return ProductManager(
        product_repository=product_repo,
        transaction_manager=transaction_manager,
        payment_method_repository=PaymentMethodRepository(session),
    )


async def get_export_manager(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ExportManager:
    return ExportManager(
        transaction_repository=TransactionRepository(session),
        payment_method_repository=PaymentMethodRepository(session),
        member_repository=MemberRepository(session),
        membership_repository=MembershipRepository(session),
    )


# ============================================================================
# Payment Method Endpoints
# ============================================================================


@payment_method_router.get("", response_model=list[PaymentMethod])
async def search_payment_methods(
    manager: Annotated[PaymentMethodManager, Depends(get_payment_method_manager)],
    request: Request,
    response: Response,
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
) -> list[PaymentMethod]:
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    result, _count = await manager.search(limit=limit, offset=offset, terms=terms)
    response.headers["X-Total-Count"] = str(_count)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    return result


@payment_method_router.get("/{id}", response_model=PaymentMethod)
async def get_payment_method(
    id: int,
    manager: Annotated[PaymentMethodManager, Depends(get_payment_method_manager)],
    request: Request,
) -> PaymentMethod:
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
    response: Response,
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
) -> list[Product]:
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    result, _count = await manager.search(limit=limit, offset=offset, terms=terms)
    response.headers["X-Total-Count"] = str(_count)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    return result


@product_router.post("", response_model=Product, status_code=status.HTTP_200_OK)
async def create_product(
    body: AbstractProduct,
    manager: Annotated[ProductManager, Depends(get_product_manager)],
    request: Request,
) -> Product:
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value)
    return await manager.product_repository.create(body)


@product_router.get("/{id}", response_model=Product)
async def get_product(
    id: int,
    manager: Annotated[ProductManager, Depends(get_product_manager)],
    request: Request,
) -> Product:
    require_role_or_ownership(request, Roles.ADMIN_READ.value)
    try:
        return await manager.get_by_id(id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@product_router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_product(
    id: int,
    body: AbstractProduct,
    manager: Annotated[ProductManager, Depends(get_product_manager)],
    request: Request,
) -> None:
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value)
    try:
        await manager.product_repository.update(body, id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@product_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: int,
    manager: Annotated[ProductManager, Depends(get_product_manager)],
    request: Request,
) -> None:
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value)
    try:
        await manager.product_repository.delete(id)
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
    require_role_or_ownership(request, Roles.ADMIN_WRITE.value)
    author_id = get_user_id(request)
    if author_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not determine authenticated user")
    await manager.buy(
        member_id=member_id,
        payment_method_id=payment_method,
        author_id=author_id,
        product_ids=products,
    )


# ============================================================================
# Transaction Endpoints
# ============================================================================


@transaction_router.get("", response_model=list[Transaction])
async def search_transactions(
    manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
    request: Request,
    response: Response,
    limit: Annotated[int, Query(ge=0)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = DEFAULT_OFFSET,
    terms: Annotated[str | None, Query()] = None,
    filter_: Annotated[str | None, Query()] = None,
    only: Annotated[str | None, Query()] = None,
) -> Any:
    require_role_or_ownership(request, Roles.TRESO_READ.value)
    filter_obj = _parse_transaction_filter(request, filter_)
    result, _count = await manager.search(
        limit=limit,
        offset=offset,
        terms=terms,
        filter_=filter_obj,
    )
    response.headers["X-Total-Count"] = str(_count)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"

    if only:
        valid_fields = {
            "id",
            "name",
            "timestamp",
            "paymentMethod",
            "value",
            "author",
            "productId",
            "productType",
            "apiKeyId",
            "membershipUuid",
        }
        requested_fields = set(only.split(","))
        invalid_fields = requested_fields - valid_fields
        if invalid_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid fields: {', '.join(invalid_fields)}",
            )
        only_fields = {"id", *requested_fields}
        return JSONResponse(
            content=[
                {k: v for k, v in item.model_dump(mode="json", by_alias=True).items() if k in only_fields}
                for item in result
            ],
            headers={
                "X-Total-Count": str(_count),
                "Access-Control-Expose-Headers": "X-Total-Count",
            },
        )

    return result


@transaction_router.post("", response_model=Transaction, status_code=status.HTTP_200_OK)
async def create_transaction(
    body: Transaction,
    manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
    request: Request,
) -> Transaction:
    require_role_or_ownership(request, Roles.TRESO_WRITE.value)
    abstract = AbstractTransaction.from_dict(body.to_dict())
    if abstract is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid transaction data")
    author_id = get_user_id(request)
    if author_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not determine authenticated user")
    abstract.author = author_id
    transaction, _created = await manager.update_or_create(abstract)
    return transaction


@transaction_router.get("/{id}", response_model=Transaction)
async def get_transaction(
    id: int,
    manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
    request: Request,
) -> Transaction:
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
    require_role_or_ownership(request, Roles.TRESO_WRITE.value)
    await manager.update_or_create(abstract_transaction=body, id=id)


@transaction_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    id: int,
    manager: Annotated[TransactionManager, Depends(get_transaction_manager)],
    request: Request,
) -> None:
    require_role_or_ownership(request, Roles.TRESO_WRITE.value)
    await manager.delete(id=id)


# ============================================================================
# Treasury Export Endpoint
# ============================================================================


@router.get(
    "/export",
    response_class=Response,
    responses={200: {"content": {"application/vnd.oasis.opendocument.spreadsheet": {}}, "description": "ODS export"}},
)
async def export_transactions(
    from_date: Annotated[date, Query(alias="fromDate")],
    to_date: Annotated[date, Query(alias="toDate")],
    manager: Annotated[ExportManager, Depends(get_export_manager)],
    request: Request,
) -> Response:
    require_role_or_ownership(request, Roles.TRESO_READ.value)
    ods_bytes = await manager.export(from_date, to_date)
    return Response(
        content=ods_bytes,
        media_type="application/vnd.oasis.opendocument.spreadsheet",
        headers={"Content-Disposition": f"attachment; filename=transactions_{from_date}_{to_date}.ods"},
    )
