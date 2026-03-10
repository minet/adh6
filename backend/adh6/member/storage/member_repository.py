"""
Implements everything related to actions on the SQL database.
"""

import calendar
import ipaddress
from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.entity import AbstractMember, Member, MemberFilter
from adh6.storage.sql.models import Modification

from ..interfaces.member_repository import MemberRepository
from .models import Adherent, Membership


class MemberSQLRepository(MemberRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_by(
        self,
        limit: int,
        offset: int,
        terms: str | None = None,
        filter_: MemberFilter | None = None,
    ) -> tuple[list[Member], int]:
        stmt = select(Adherent)

        if filter_:
            if filter_.ip:
                stmt = stmt.where(Adherent.ip == filter_.ip)
            if filter_.since:
                stmt = stmt.where(Adherent.date_de_depart >= filter_.since)
            if filter_.until:
                stmt = stmt.where(Adherent.date_de_depart <= filter_.until)
            if filter_.membership:
                stmt = stmt.join(Membership, Membership.adherent_id == Adherent.id).where(
                    Membership.status == filter_.membership
                )

        if terms:
            terms_lower = terms.lower()
            parts = terms_lower.split(None, 1)  # split into at most 2 words
            full_name_match = None
            if len(parts) == 2:
                a, b = parts
                # "firstname lastname" or "lastname firstname"
                full_name_match = (func.lower(Adherent.prenom).contains(a) & func.lower(Adherent.nom).contains(b)) | (
                    func.lower(Adherent.prenom).contains(b) & func.lower(Adherent.nom).contains(a)
                )
            stmt = stmt.where(
                (func.lower(Adherent.nom).contains(terms_lower))
                | (func.lower(Adherent.prenom).contains(terms_lower))
                | (func.lower(Adherent.mail).contains(terms_lower))
                | (func.lower(Adherent.login).contains(terms_lower))
                | (func.lower(Adherent.commentaires).contains(terms_lower))
                | (Adherent.ip.contains(terms))
                | (Adherent.subnet.contains(terms))
                | (full_name_match if full_name_match is not None else False)
            )

        # Count
        count_result = await self.session.execute(stmt)
        count = len(count_result.all())

        # Apply ordering and pagination
        stmt = stmt.order_by(Adherent.login.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return list(map(_map_member_sql_to_entity, r)), count

    async def get_by_id(self, object_id: int) -> Member | None:
        stmt = select(Adherent).where(Adherent.id == object_id)
        adh = await self.session.scalar(stmt)
        return _map_member_sql_to_entity(adh) if adh else None

    async def get_by_login(self, login: str) -> Member | None:
        stmt = select(Adherent).where(Adherent.login == login)
        adh = await self.session.scalar(stmt)
        return _map_member_sql_to_entity(adh) if adh else None

    async def create(self, object_to_create: Member) -> object:
        now = datetime.now()
        member: Adherent = Adherent(
            nom=object_to_create.last_name,
            prenom=object_to_create.first_name,
            mail=object_to_create.email,
            login=object_to_create.username,
            created_at=now,
            updated_at=now,
            commentaires=object_to_create.comment,
            date_de_depart=object_to_create.departure_date,
        )

        self.session.add(member)
        await self.session.flush()  # Ensure the member gets an ID
        # Map to entity while still in session context
        result = _map_member_sql_to_entity(member)

        return result

    async def update(self, abstract_member: AbstractMember, override=False) -> object:
        stmt = select(Adherent).where(Adherent.id == abstract_member.id)
        adherent = await self.session.scalar(stmt)
        if adherent is None:
            from adh6.exceptions import MemberNotFoundError

            raise MemberNotFoundError(abstract_member.id)

        new_adherent = _merge_sql_with_entity(abstract_member, adherent, override)
        await self._record_modification(
            adherent_id=new_adherent.id,
            action=f"member: updated {new_adherent.login}",
        )
        await self.session.flush()
        mapped_member = _map_member_sql_to_entity(new_adherent)

        return mapped_member

    async def delete(self, member_id) -> None:
        stmt = select(Adherent).where(Adherent.id == member_id)
        member = await self.session.scalar(stmt)
        if not member:
            raise ValueError(f"Member {member_id} not found")
        await self._record_modification(
            adherent_id=member.id,
            action=f"member: deleted {member.login}",
        )
        await self.session.delete(member)

    async def _record_modification(self, adherent_id: int, action: str) -> None:
        now = datetime.now()
        self.session.add(
            Modification(
                adherent_id=adherent_id,
                action=action,
                created_at=now,
                updated_at=now,
                utilisateur_id=None,
            )
        )

    async def update_password(self, member_id, hashed_password):
        stmt = select(Adherent).where(Adherent.id == member_id)
        adherent = await self.session.scalar(stmt)

        if not adherent:
            raise ValueError(f"Member {member_id} not found")

        adherent.password = hashed_password

    async def add_duration(self, member_id: int, duration_in_mounth: int) -> None:
        now = date.today()

        stmt = select(Adherent).where(Adherent.id == member_id)
        adherent = await self.session.scalar(stmt)

        if not adherent:
            raise ValueError(f"Member {member_id} not found")
        if adherent.date_de_depart is None or adherent.date_de_depart < now:
            adherent.date_de_depart = now

        days_to_add = 0
        for i in range(duration_in_mounth):
            if adherent.date_de_depart.month + i <= 12:
                days_to_add += calendar.monthrange(adherent.date_de_depart.year, adherent.date_de_depart.month + i)[1]
            else:
                days_to_add += calendar.monthrange(
                    adherent.date_de_depart.year + 1,
                    adherent.date_de_depart.month + i - 12,
                )[1]
        adherent.date_de_depart += timedelta(days=days_to_add)

    async def used_wireless_public_ips(self) -> list[ipaddress.IPv4Address]:
        stmt = select(Adherent.ip).where(Adherent.ip.is_not(None))
        result = await self.session.execute(stmt)
        r = result.all()
        return [ipaddress.IPv4Address(i[0]) for i in r if i[0] is not None]

    async def update_comment(self, member_id: int, comment: str) -> None:
        stmt = select(Adherent).where(Adherent.id == member_id)
        adherent = await self.session.scalar(stmt)
        if not adherent:
            raise ValueError(f"Member {member_id} not found")
        adherent.commentaires = comment


def _merge_sql_with_entity(entity: AbstractMember, sql_object: Adherent, override=False) -> Adherent:
    now = datetime.now()
    adherent = sql_object
    if entity.email is not None or override:
        adherent.mail = entity.email
    if entity.username is not None or override:
        adherent.login = entity.username
    if entity.first_name is not None or override:
        adherent.prenom = entity.first_name
    if entity.last_name is not None or override:
        adherent.nom = entity.last_name
    if entity.ip is not None or override:
        adherent.ip = entity.ip if entity.ip != "" else None  # type: ignore  # TODO: typing
    if entity.subnet is not None or override:
        adherent.subnet = entity.subnet if entity.subnet != "" else None  # type: ignore  # TODO: typing
    if entity.comment is not None or override:
        adherent.commentaires = entity.comment

    adherent.updated_at = now
    return adherent


def _map_member_sql_to_abstract_entity(adh: Adherent) -> AbstractMember:
    """
    Map a Adherent object from SQLAlchemy to a Member (from the entity folder/layer).
    """
    midnight = time(0, 0, 0)
    date_depart_datetime = datetime.combine(adh.date_de_depart, midnight) if adh.date_de_depart else None
    return AbstractMember(
        id=adh.id,
        username=adh.login,
        email=adh.mail,
        firstName=adh.prenom,
        lastName=adh.nom,
        departureDate=date_depart_datetime,
        comment=adh.commentaires,
        ip=adh.ip,
        subnet=adh.subnet,
        mailinglist=adh.mail_membership,
    )


def _map_member_sql_to_entity(adh: Adherent) -> Member:
    """
    Map a Adherent object from SQLAlchemy to a Member (from the entity folder/layer).
    """
    return Member(
        id=adh.id,
        username=adh.login or "",
        email=adh.mail or "",
        firstName=adh.prenom or "",
        lastName=adh.nom or "",
        departureDate=datetime.combine(adh.date_de_depart, time.min) if adh.date_de_depart else None,
        comment=adh.commentaires,
        ip=adh.ip,
        subnet=adh.subnet,
        mailinglist=adh.mail_membership,
    )
