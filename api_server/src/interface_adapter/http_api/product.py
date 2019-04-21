from src.interface_adapter.http_api.decorator.auth import auth_regular_admin
from src.interface_adapter.http_api.decorator.sql_session import require_sql


@require_sql
@auth_regular_admin
def search(limit=100, offset=0, terms=None):
    pass


@require_sql
@auth_regular_admin
def post(body):
    pass


@require_sql
@auth_regular_admin
def get(product_id):
    pass


@require_sql
@auth_regular_admin
def patch(product_id, body):
    pass