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
def filter_product(limit=100, offset=0, terms=None, name=None):
    #pass
    s = g.session
    if limit < 0:
        return "Limit must be positive", 400

    q = s.query(Product)
    if name:
        q = q.filter(Product.name == name)

    if terms:
        q = q.filter(
                (Product.id.contains(terms)) |
                (Product.buying_price.contains(terms)) |
                (Product.selling_price.contains(terms)) |
                (Product.name.contains(terms))
        )
    count = q.count()
    q = q.order_by(Product.name.asc())
    q = q.offset(offset)
    q = q.limit(limit)
    r = q.all()
    headers = {
            "X-Total-Count": str(count),
            'access-control-expose-headers': 'X-Total-Count'
    }
    logging.info("%s fetched the product list", g.admin.login)
    return list(map(dict, r)), 200, headers

@require_sql
@auth_regular_admin
def create_product(body):
    pass

@require_sql
@auth_regular_admin
def get_product(product_id):
    s = g.session
    try:
        logging.info("%s fetched the product %s", g.admin.login, product_id)
        return dict(Product.find(s, product_id)), 200
    except ProductNotFound:
        return NoContent, 404

