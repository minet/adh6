from adh.auth import auth_regular_admin
from adh.util.session_decorator import require_sql

@require_sql
@auth_regular_admin
def search(limit=100, offset=0, terms=None, account=None):
    pass

@require_sql
@auth_regular_admin
def create_transaction(body):
    pass

@require_sql
@auth_regular_admin
def get(body):
    pass

@require_sql
@auth_regular_admin
def delete(transaction_id):
    pass
