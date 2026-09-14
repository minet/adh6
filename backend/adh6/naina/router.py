from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import Roles
from adh6.database import get_session
from adh6.entity import Naina
from adh6.exceptions import NotFoundError
from adh6.member.storage import MemberRepository
from adh6.security import get_token_info, require_role_or_ownership

from .manager import NainaManager
from .storage import NainaSQLRepository

router = APIRouter(prefix="/naina", tags=["naina"])


async def get_naina_manager(session: Annotated[AsyncSession, Depends(get_session)]) -> NainaManager:
    return NainaManager(
        repository=NainaSQLRepository(session),
        member_repository=MemberRepository(session),
    )


@router.get("", response_model=list[Naina])
async def search_nainas(
    manager: Annotated[NainaManager, Depends(get_naina_manager)],
    request: Request,
) -> list[Naina]:
    require_role_or_ownership(request, Roles.NETWORK_READ.value)
    return await manager.search()


@router.post("/{identifier}", status_code=status.HTTP_201_CREATED, response_class=Response)
async def create_naina(
    identifier: str,
    manager: Annotated[NainaManager, Depends(get_naina_manager)],
    request: Request,
) -> Response:
    _require_naina_admin(request)
    try:
        await manager.create(identifier)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_201_CREATED)


@router.delete("/{identifier}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def revoke_naina(
    identifier: str,
    manager: Annotated[NainaManager, Depends(get_naina_manager)],
    request: Request,
) -> Response:
    _require_naina_admin(request)
    await manager.revoke(identifier)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _require_naina_admin(request: Request) -> None:
    if get_token_info(request).get("auth_method") == "api_key":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API keys cannot manage NainAs")
    require_role_or_ownership(request, Roles.ADMIN_PROD.value)
