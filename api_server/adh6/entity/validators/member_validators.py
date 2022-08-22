from datetime import datetime

from sqlalchemy import false

from adh6.entity import Member

from adh6.room.storage.room_repository import RoomSQLRepository as RoomRepository


def is_member_active(ctx, member: Member):
    if member.departure_date is None:
        return false

    if isinstance(member.departure_date, datetime):
        member_departure = member.departure_date.date()
    else:
        member_departure = member.departure_date
    return member_departure > datetime.now().date() and RoomRepository().get_from_member(ctx, member.id) is not None


def has_member_subnet(member: Member):
    return member.ip is not None and member.subnet is not None
