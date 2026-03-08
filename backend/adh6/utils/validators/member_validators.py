import re
from datetime import datetime

from adh6.entity import Member
from sqlalchemy import false


def is_member_active(member: Member):
    if member.departure_date is None:
        return False

    if isinstance(member.departure_date, datetime):
        member_departure = member.departure_date.date()
    else:
        member_departure = member.departure_date
    return member_departure > datetime.now().date()


def is_password_valid(password: str) -> bool:
    """These checks or run on the frontend to give instant feedback to the user and on the backend as a HTTP request could be sent with an invalid password."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[\"'#!@$%^&(){}[\]:;<>,.*?/~_+\-=\|]", password):
        return False
    return not len(password) > 64


def has_member_subnet(member: Member):
    return member.ip is not None and member.subnet is not None
