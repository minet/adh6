import datetime
import json
import logging
import requests

import dateutil
from connexion import NoContent
from flask import g
from sqlalchemy.orm.exc import MultipleResultsFound

from adh.auth import auth_regular_admin
from adh.model import models
from adh.util.session_decorator import require_sql

@require_sql
@auth_regular_admin
def filter_account(limit=100, offset=0, terms=None, name=None, type=None):
    s = g.session
    if limit < 0:
        return "Limit must be positive", 400

    q = s.query(Account)

    if name and type:
        q = q.filter(
                (Account.name == name) &
                (Account.type == type)
            )
    if name:
        q = q.filter(Account.name == name)      
    if type:
        q = q.filter(Account.type == type)

    if terms:
        q = q.filter(
            (Account.id.contains(terms)) |
            (Account.name.contains(terms)) |
            (Account.type.contains(terms)) |
            (Account.actif.contains(terms))
        )
    count = q.count()
    q = q.order_by(Account.name.asc())
    q = q.offset(offset)
    q = q.limit(limit)
    r = q.all()
    headers = {
        "X-Total-Count": str(count),
        'access-control-expose-headers': 'X-Total-Count'
    }
    logging.info("%s fetched the account list", g.admin.login)
    return list(map(dict, r)), 200, headers

@require_sql
@auth_regular_admin
def create_account(body):
    pass

@require_sql
@auth_regular_admin
def get_account(account_id):
    s = g.session
    try:
        logging.info("%s fetched the account %s", g.admin.login, username)
        return dict(Account.find(s, account_id)), 200
    except AccountNotFound:
        return NoContent, 404

@require_sql
@auth_regular_admin
def patch_account(account_id, body):
    s = g.session

    update = account_exists(s, account_id)

    if not update:
        return NoContent, 404

    account = Account.find(s, account_id)
    account.start_modif_tracking()
    try:
        account.name = body.get("name", account.name)
        account.type = body.get("type", account.type)
        account.actif = body.get("actif", account.type)
    # Erreurs non gérées

    Modification.add(s, account, g.admin)
    logging.info("%s updated the account %s\n%s",
            g.admin.login, account_id, json.dumps(body, sort_keys=True)
            #json.dumps prend le texte du body et le met sous le bon format
    )
    return NoContent, 204
