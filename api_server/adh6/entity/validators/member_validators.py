from datetime import datetime

from sqlalchemy import false

from adh6.entity import Member


def is_member_active(member: Member):
    if member.departure_date is None:
        return false

    if isinstance(member.departure_date, datetime):
        member_departure = member.departure_date.date()
    else:
        member_departure = member.departure_date
    return member_departure > datetime.now().date()


def has_member_subnet(member: Member):
    return member.ip is not None and member.subnet is not None
