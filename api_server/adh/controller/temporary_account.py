import datetime
import logging
import secrets

from connexion import NoContent
from flask import g

from adh.auth import auth_super_admin
from adh.model.models import NainA
from adh.util.session_decorator import require_sql

TOKEN_SIZE = 32


@require_sql
@auth_super_admin
def create_temp_account(body):
    s = g.session
    firstname = body.get("firstname")
    lastname = body.get("lastname")
    if not firstname or not lastname:
        return "Empty first or last name", 400

    token = secrets.token_urlsafe(TOKEN_SIZE)
    now = datetime.datetime.now()
    end = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=20, minute=0)
    naina = NainA(
        first_name=firstname,
        last_name=lastname,
        access_token=token,
        start_time=now,
        expiration_time=end,
        admin=g.admin.login,
    )
    s.add(naina)

    logging.info("%s created a temporary account for '%s %s'", g.admin.login, firstname, lastname)

    return {"accessToken": "NAINA_{}".format(token)}, 200


@require_sql
@auth_super_admin
def revoke_temp_account():
    s = g.session

    now = datetime.datetime.now()
    q = s.query(NainA)
    q = q.filter(NainA.expiration_time > now)
    q.update({"expiration_time": now})
    s.commit()
    logging.info("%s revoked all temporary accounts.", g.admin.login)
    return NoContent, 204