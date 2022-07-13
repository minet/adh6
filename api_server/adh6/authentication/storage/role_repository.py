
import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.sql import Select
from adh6.authentication import AuthenticationMethod, Roles
from adh6.authentication.storage.models import ApiKey, AuthenticationRoleMapping
from adh6.authentication.interfaces.role_repository import RoleRepository
from adh6.storage import db


class RoleSQLRepository(RoleRepository):
    def get_roles(self, method: AuthenticationMethod = ..., roles: List[str] = ...) -> List[Roles]:
        if method == AuthenticationMethod.NONE or not roles:
            return []
        smt: Select = select(AuthenticationRoleMapping.role).where(AuthenticationRoleMapping.name.in_(roles))
        return [i[0].value for i in db.session().execute(smt).all()]

    def get_api_key_user(self, api_key: str) -> str:
        smt: Select = select(ApiKey.name).where(ApiKey.uuid == api_key)
        return db.session().execute(smt).scalar()
        
