from typing import List

from sqlalchemy import select
from sqlalchemy.sql import Select
from adh6.authentication import AuthenticationMethod, Roles
from adh6.authentication.storage.models import ApiKey, AuthenticationRoleMapping
from adh6.authentication.interfaces.role_repository import RoleRepository
from adh6.storage import db
from adh6.storage.sql.models import Adherent


class RoleSQLRepository(RoleRepository):
    def get_roles(self, user_name: str, method: AuthenticationMethod = AuthenticationMethod.NONE, roles: List[str] = []) -> List[Roles]:
        if method == AuthenticationMethod.NONE or not roles:
            return []
        smt: Select = select(AuthenticationRoleMapping.role).where(AuthenticationRoleMapping.name.in_(roles))
        all_roles = [i[0] for i in db.session().execute(smt).all()]
        smt = select(Adherent.is_naina).where((Adherent.login == user_name) | (Adherent.ldap_login == user_name))
        is_naina = db.session().execute(smt).scalar()
        if is_naina:
            if Roles.ADMIN_READ not in all_roles:
                all_roles.append(Roles.ADMIN_READ)
            if Roles.ADMIN_WRITE not in all_roles:
                all_roles.append(Roles.ADMIN_WRITE)
        return [i.value for i in all_roles]

    def get_api_key_user(self, api_key: str) -> str:
        smt: Select = select(ApiKey.name).where(ApiKey.uuid == api_key)
        return db.session().execute(smt).scalar()

    def get_user_id(self, user_name: str) -> int:
        smt = select(Adherent.id).where((Adherent.login == user_name) | (Adherent.ldap_login == user_name))
        return db.session().execute(smt).scalar()
        
