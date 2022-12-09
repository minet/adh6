
from adh6.entity import Member


def is_member_active(member: Member) -> bool:
    from datetime import datetime
    from adh6.room.storage.room_repository import RoomSQLRepository as RoomRepository
    
    if member.departure_date is None:
        return False

    if isinstance(member.departure_date, datetime):
        member_departure = member.departure_date.date()
    else:
        member_departure = member.departure_date
    return member_departure > datetime.now().date() and RoomRepository().get_from_member(member) is not None


def has_member_subnet(member: Member):
    return member.ip is not None and member.subnet is not None
