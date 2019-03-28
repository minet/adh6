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
# from adh.exceptions import AccountTypeNotFound
# def account_type_exists(s, account_type_id):


@require_sql
@auth_regular_admin
def filter_account_type(limit=100, offset=0, terms=None):
    """ [API] Filter the list of account types from the the database"""
    s = g.session
    if limit < 0:
        return "Limit must be positive", 400
    
    q = s.query(AccountType)
    if terms:
        q = q.filter(
                (AccountType.name.contains(terms))
        )
    count = q.count()
    q = q.order_by(AccountType.name.asc())
    q = q.offset(offset)
    q = q.limit(limit)
    r = q.all()
    headers = {
        "X-Total-Count": str(count),
        'access-control-expose-headers': 'X-Total-Count'
    }
    logging.info("%s fetched the account type list", g.admin.login)
    return list(map(dict, r)), 200, headers

@require_sql
@auth_regular_admin
def create_account_type(body):
    pass

@require_sql
@auth_regular_admin
def get_account_type(account_type_id):
    """ [API] Get the specified account type from the database """
    s = g.session
    try:
        logging.info("%s fetched the account type %s", g.admin.login, account_type_id)
        return dict(AccountType.find(s, account_type_id)), 200
    except AccountTypeNotFound:
        return NoContent, 404


@require_sql
@auth_regular_admin
def patch_account_type(account_type_id, body):
    """ [API] Update an account type from the database """
    s = g.session

    # Create a valid object

    # Check if it already exists
    update = account_type_exists(s, account_type_id)

    if not update:
        return NoContent, 404

    account_type = AccountType.find(s, account_type_id)
    account_type.start_modif_tracking()
    try:
        account_type.name = body.get("name", account_type.name)
    except ValueError:
        return "String must not be empty", 400

    # Create the corresponding modification
    Modification.add(s, account_type, g.admin)

    logging.info("%s updated the account_type %s\n%s",
                 g.admin.login, account_type_id, json.dumps(body, sort_keys=True))
    return NoContent, 204

