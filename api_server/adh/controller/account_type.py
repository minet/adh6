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
from adh.exceptions import AccountTypeNotFound


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
    """ [API] Create account type from the database """
    s = g.session

    # Create a valid object
    try:
        new_account_type = AccountType.from_dict(s, body)
    except ValueError:
        return "String must not be empty", 400

    new_account_type = s.merge(new_account_type)

    # Create the corresponding modification
    Modification.add(s, new_account_type, g.admin)

    logging.info("%s created the account type \n%s",
                g.admin.login, json.dumps(body, sort_keys=True))
    return NoContent, 201


@require_sql
@auth_regular_admin
def get_account_type(account_type_id):
    """ [API] Get the specified account type from the database """
    s = g.session
    try:
        result = AccountType.find(s, account_type_id)
    except AccountTypeNotFound:
        return NoContent, 404

    result = dict(result)
    logging.info("%s fetched the account type %s",
                 g.admin.login, account_type_id)
    return result, 200


@require_sql
@auth_regular_admin
def update_account_type(account_type_id, body):
    """ [API] Update an account type from the database """
    if "id" in body:
        return "You cannot update the id", 400

    name = body["name"]
    s = g.session

    try:
        new_account_type = AccountType.find(s, account_type_id)
    except AccountTypeNotFound:
        return "Account type not found", 400

    new_account_type.name = name

    # Build the corresponding modification
    Modification.add(s, new_account_type, g.admin)

    logging.info("%s updated the account type %s",
                 g.admin.login, account_type_id)
    return NoContent, 204
