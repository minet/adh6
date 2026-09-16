"""
Implements everything related to actions on the SQL database.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import Select, String, and_, cast, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import MiniRouter, MiniRouterLoan
from adh6.exceptions import MiniRouterLoanNotFoundError, MiniRouterNotFoundError
from adh6.member.storage.models import Adherent
from adh6.room.storage.models import Chambre, RoomMemberLink
from adh6.storage.count import count_rows

from ..addresses import addresses_of, number_from_terms
from ..interfaces import MiniRouterRepository
from .models import MiniRouter as SQLMiniRouter, MiniRouterLoan as SQLMiniRouterLoan

UNIQUE_FIELDS = {
    "hardware_mac": SQLMiniRouter.hardware_mac,
    "number": SQLMiniRouter.number,
}

Author = aliased(Adherent)


class MiniRouterSQLRepository(MiniRouterRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_by(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        terms: str | None = None,
        loaned: bool | None = None,
        overdue: bool | None = None,
    ) -> tuple[list[MiniRouter], int]:
        current_loan = and_(
            SQLMiniRouterLoan.mini_router_id == SQLMiniRouter.id,
            SQLMiniRouterLoan.returned_at.is_(None),
        )
        stmt = select(SQLMiniRouter)

        terms = (terms or "").strip().lower()
        if terms:
            matching_member = exists().where(
                current_loan,
                Adherent.id == SQLMiniRouterLoan.member_id,
                or_(
                    func.lower(Adherent.nom).contains(terms, autoescape=True),
                    func.lower(Adherent.prenom).contains(terms, autoescape=True),
                    func.lower(Adherent.login).contains(terms, autoescape=True),
                ),
            )
            matching_room = exists().where(
                current_loan,
                RoomMemberLink.member_id == SQLMiniRouterLoan.member_id,
                Chambre.id == RoomMemberLink.room_id,
                cast(Chambre.numero, String).startswith(terms, autoescape=True),
            )
            criteria = [
                func.lower(SQLMiniRouter.hardware_mac).contains(terms.replace("-", ":"), autoescape=True),
                matching_member,
                matching_room,
            ]
            number = number_from_terms(terms)
            if number is not None:
                criteria.append(SQLMiniRouter.number == number)
            stmt = stmt.where(or_(*criteria))

        if loaned is not None:
            has_loan = exists().where(current_loan)
            stmt = stmt.where(has_loan if loaned else ~has_loan)

        if overdue is not None:
            late_loan = exists().where(current_loan, SQLMiniRouterLoan.due_date < date.today())
            stmt = stmt.where(late_loan if overdue else ~late_loan)

        count = await count_rows(self.session, stmt)

        stmt = stmt.order_by(SQLMiniRouter.id.asc()).offset(offset).limit(limit)
        mini_routers = list((await self.session.execute(stmt)).scalars().all())
        return await self._map_mini_routers(mini_routers), count

    async def get_by_id(self, object_id: int) -> MiniRouter | None:
        mini_router = await self.session.get(SQLMiniRouter, object_id)
        if mini_router is None:
            return None
        return (await self._map_mini_routers([mini_router]))[0]

    async def is_taken(self, field: str, value: str | int, exclude_id: int | None = None) -> bool:
        stmt = select(SQLMiniRouter.id).where(UNIQUE_FIELDS[field] == value)
        if exclude_id is not None:
            stmt = stmt.where(SQLMiniRouter.id != exclude_id)
        return await self.session.scalar(stmt.limit(1)) is not None

    async def create(self, mini_router: MiniRouter) -> MiniRouter:
        sql_mini_router = SQLMiniRouter()
        _merge_mini_router(sql_mini_router, mini_router)
        self.session.add(sql_mini_router)
        await self.session.flush()
        return (await self._map_mini_routers([sql_mini_router]))[0]

    async def update(self, object_id: int, mini_router: MiniRouter) -> MiniRouter:
        sql_mini_router = await self.session.get(SQLMiniRouter, object_id)
        if sql_mini_router is None:
            raise MiniRouterNotFoundError(object_id)
        _merge_mini_router(sql_mini_router, mini_router)
        await self.session.flush()
        return (await self._map_mini_routers([sql_mini_router]))[0]

    async def delete(self, object_id: int) -> None:
        sql_mini_router = await self.session.get(SQLMiniRouter, object_id)
        if sql_mini_router is None:
            raise MiniRouterNotFoundError(object_id)
        loans = await self.session.scalars(
            select(SQLMiniRouterLoan).where(SQLMiniRouterLoan.mini_router_id == object_id)
        )
        for loan in loans:
            await self.session.delete(loan)
        await self.session.delete(sql_mini_router)
        await self.session.flush()

    async def list_loans(self, mini_router_id: int | None = None, member_id: int | None = None) -> list[MiniRouterLoan]:
        stmt = _select_loans().order_by(SQLMiniRouterLoan.started_at.desc(), SQLMiniRouterLoan.id.desc())
        if mini_router_id is not None:
            stmt = stmt.where(SQLMiniRouterLoan.mini_router_id == mini_router_id)
        if member_id is not None:
            stmt = stmt.where(SQLMiniRouterLoan.member_id == member_id)
        return [_map_loan(*row) for row in (await self.session.execute(stmt)).tuples().all()]

    async def get_loan(self, loan_id: int) -> MiniRouterLoan | None:
        row = (await self.session.execute(_select_loans().where(SQLMiniRouterLoan.id == loan_id))).tuples().first()
        return _map_loan(*row) if row else None

    async def create_loan(self, mini_router_id: int, loan: MiniRouterLoan, author_id: int) -> MiniRouterLoan:
        sql_loan = SQLMiniRouterLoan(mini_router_id=mini_router_id, member_id=loan.member, author_id=author_id)
        _merge_loan(sql_loan, loan)
        self.session.add(sql_loan)
        await self.session.flush()
        return await self._reload_loan(sql_loan.id)

    async def update_loan(self, loan_id: int, loan: MiniRouterLoan) -> MiniRouterLoan:
        sql_loan = await self.session.get(SQLMiniRouterLoan, loan_id)
        if sql_loan is None:
            raise MiniRouterLoanNotFoundError(loan_id)
        _merge_loan(sql_loan, loan)
        await self.session.flush()
        return await self._reload_loan(loan_id)

    async def _reload_loan(self, loan_id: int) -> MiniRouterLoan:
        loan = await self.get_loan(loan_id)
        if loan is None:
            raise MiniRouterLoanNotFoundError(loan_id)
        return loan

    async def _map_mini_routers(self, mini_routers: list[SQLMiniRouter]) -> list[MiniRouter]:
        """Attach the current loan, the room of its member and the pending deposits to each mini-router."""
        ids = [m.id for m in mini_routers]
        loans: dict[int, MiniRouterLoan] = {}
        rooms: dict[int, Chambre] = {}
        ids_to_refund: set[int] = set()
        if ids:
            refund_stmt = select(SQLMiniRouterLoan.mini_router_id).where(
                SQLMiniRouterLoan.mini_router_id.in_(ids),
                SQLMiniRouterLoan.returned_at.is_not(None),
                SQLMiniRouterLoan.deposit_status == "held",
            )
            ids_to_refund = set((await self.session.scalars(refund_stmt)).all())

            stmt = _select_loans().where(
                SQLMiniRouterLoan.mini_router_id.in_(ids), SQLMiniRouterLoan.returned_at.is_(None)
            )
            for row in (await self.session.execute(stmt)).tuples().all():
                loans[row[0].mini_router_id] = _map_loan(*row)

            member_ids = [loan.member for loan in loans.values()]
            if member_ids:
                room_stmt = (
                    select(RoomMemberLink.member_id, Chambre)
                    .join(Chambre, Chambre.id == RoomMemberLink.room_id)
                    .where(RoomMemberLink.member_id.in_(member_ids))
                )
                rooms = dict((await self.session.execute(room_stmt)).tuples().all())

        result = []
        for m in mini_routers:
            loan = loans.get(m.id)
            room = rooms.get(loan.member) if loan and loan.member is not None else None
            addresses = addresses_of(m.number) if m.number is not None else None
            result.append(
                MiniRouter(
                    id=m.id,
                    hardwareMac=m.hardware_mac,
                    number=m.number,
                    ipWireguard=addresses.ip_wireguard if addresses else None,
                    ipVlan31=addresses.ip_vlan31 if addresses else None,
                    macAccept=addresses.mac_accept if addresses else None,
                    macDeny=addresses.mac_deny if addresses else None,
                    model=m.model,
                    configState=m.config_state,
                    comment=m.comment,
                    roomId=room.id if room else None,
                    roomNumber=room.numero if room else None,
                    depositToRefund=m.id in ids_to_refund,
                    currentLoan=loan,
                )
            )
        return result


def _select_loans() -> Select[tuple[SQLMiniRouterLoan, Adherent, Adherent, str]]:
    return (
        select(SQLMiniRouterLoan, Adherent, Author, SQLMiniRouter.hardware_mac)
        .join(SQLMiniRouter, SQLMiniRouter.id == SQLMiniRouterLoan.mini_router_id)
        .outerjoin(Adherent, Adherent.id == SQLMiniRouterLoan.member_id)
        .outerjoin(Author, Author.id == SQLMiniRouterLoan.author_id)
    )


def _merge_mini_router(sql_mini_router: SQLMiniRouter, mini_router: MiniRouter) -> None:
    sql_mini_router.hardware_mac = mini_router.hardware_mac
    sql_mini_router.number = mini_router.number
    sql_mini_router.model = mini_router.model
    sql_mini_router.config_state = mini_router.config_state
    sql_mini_router.comment = mini_router.comment


def _merge_loan(sql_loan: SQLMiniRouterLoan, loan: MiniRouterLoan) -> None:
    sql_loan.started_at = loan.started_at
    sql_loan.due_date = loan.due_date
    sql_loan.returned_at = loan.returned_at
    sql_loan.deposit_amount = Decimal(str(loan.deposit_amount))
    sql_loan.payment_method_id = loan.payment_method
    if loan.deposit_status is not None:
        sql_loan.deposit_status = loan.deposit_status


def _full_name(member: Adherent | None) -> str | None:
    if member is None:
        return None
    return " ".join(part for part in (member.prenom, member.nom) if part) or None


def _map_loan(
    loan: SQLMiniRouterLoan, member: Adherent | None, author: Adherent | None, hardware_mac: str
) -> MiniRouterLoan:
    return MiniRouterLoan(
        id=loan.id,
        miniRouter=loan.mini_router_id,
        miniRouterHardwareMac=hardware_mac,
        member=loan.member_id,
        memberName=_full_name(member),
        startedAt=loan.started_at,
        dueDate=loan.due_date,
        returnedAt=loan.returned_at,
        depositAmount=float(loan.deposit_amount),
        paymentMethod=loan.payment_method_id,
        depositStatus=loan.deposit_status,
        author=loan.author_id,
        authorName=_full_name(author),
        overdue=loan.returned_at is None and loan.due_date is not None and loan.due_date < date.today(),
    )
