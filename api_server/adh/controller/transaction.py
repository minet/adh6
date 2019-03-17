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
def filter_transaction(limit=100, offset=0, terms=None, account=None):
    """ [API] Filter the list of transactions from the the database """
    s = g.session
    if limit < 0:
        return "Limit must be positive", 400

    q = s.query(Transaction)
    if account:
        q = q.filter(Transaction.src == account | Transaction.dst == account)
    if terms:
        q = q.filter(
            (Transaction.name.contains(terms)) |
            (Transaction.attachmentscontains(terms))
        )
    count = q.count()
    q = q.order_by(Transaction.timestamp.desc())
    q = q.offset(offset)
    q = q.limit(limit)
    r = q.all()
    headers = {
        "X-Total-Count": str(count),
        'access-control-expose-headers': 'X-Total-Count'
    }
    logging.info("%s fetched the transaction list", g.admin.login)
    return list(map(dict, r)), 200, headers

@require_sql
@auth_regular_admin
def create_transaction(body):
    """ [API] Create transaction from the database """
    s = g.session

    # Create a valid object
    try:
        new_transaction = Transaction.from_dict(s, body)
    except ValueError:
        return "String must not be empty", 400

    new_transaction = s.merge(new_member)

    # Create the corresponding modification
    Modification.add(s, new_transaction, g.admin)

    logging.info("%s created the transaction \n%s",
                g.admin.login, json.dumps(body, sort_keys=True))
    return NoContent, 201

@require_sql
@auth_regular_admin
def get_transaction(transaction_id):
    """ [API] Get the specified transaction from the database """
    s = g.session
    try:
        logging.info("%s fetched the transaction %s", g.admin.login, username)
        return dict(Transaction.find(s, transaction_id)), 200
    except TransactionNotFound:
        return NoContent, 404

@require_sql
@auth_regular_admin
def delete_transaction(transaction_id):
    """ [API] Delete the specified transaction from the database """
    s = g.session

    # Find the soon-to-be deleted transaction
    try:
        a = Transaction.find(s, transaction_id)
    except TransactionNotFound:
        return NoContent, 404

    try:
        # if so, start tracking for modifications
        a.start_modif_tracking()

        # Actually delete it
        s.delete(a)

        # Write it in the modification table
        Modification.add(s, a, g.admin)
    except Exception:
        raise
    logging.info("%s deleted the transaction %s", g.admin.login, username)
    return NoContent, 204
