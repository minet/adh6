from datetime import datetime

from src.entity import Member
from src.entity.null import Null


def is_member_active(member: Member):
    print(member.departure_date)
    return member.departure_date is not None and member.departure_date > datetime.now().date() and not isinstance(
        member.room,
        Null)


def has_member_subnet(member: Member):
    return member.ip is not None and member.subnet is not None
