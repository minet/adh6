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
# from adh.expections import PaymentMethodNotFound
# def payment_method_exists(s, payment_method_id):

@require_sql
@auth_regular_admin
def filter_payment_methods(limit=100, offset=0, terms=None):
    """ [API] Filter the list of payment methods from the the database """
    s = g.session
    if limit < 0:
        return "Limit must be positive", 400

    q = s.query(PaymentMethod)
    if terms:
        q = q.filter(
            (PaymentMethod.name.contains(terms))
        )
    count = q.count()
    q = q.order_by(PaymentMethod.name.asc())
    q = q.offset(offset)
    q = q.limit(limit)
    r = q.all()
    headers = {
        "X-Total-Count": str(count),
        'access-control-expose-headers': 'X-Total-Count'
    }
    logging.info("%s fetched the payment method list", g.admin.login)
    return list(map(dict, r)), 200, headers

@require_sql
@auth_regular_admin
def create_payment_method(body):
    pass

@require_sql
@auth_regular_admin
def get_payment_method(payment_method_id):
    """ [API] Get the specified payment method from the database """
    s = g.session
    try:
        logging.info("%s fetched the payment method %s", g.admin.login, payment_method_id)
        return dict(PaymentMethod.find(s, payment_method_id)), 200
    except PaymentMethodNotFound:
        return NoContent, 404


@require_sql
@auth_regular_admin
def patch_payment_method(payment_method_id, body):
    """ [API] Update a payment method from the database """
    s = g.session

    # Create a valid object

    # Check if it already exists
    update = payment_method_exists(s, payment_method_id)

    if not update:
        return NoContent, 404

    payment_method = AccountType.find(s, payment_method_id)
    payment_method.start_modif_tracking()
    try:
        payment_method.name = body.get("name", payment_method.name)
    except ValueError:
        return "String must not be empty", 400

    # Create the corresponding modification
    Modification.add(s, payment_method, g.admin)

    logging.info("%s updated the payment method %s\n%s",
                 g.admin.login, payment_method_id, json.dumps(body, sort_keys=True))
    return NoContent, 204


