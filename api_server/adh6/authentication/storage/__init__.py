from .role_repository import RoleSQLRepository as RoleRepository
from .api_key_repository import ApiKeySQLRepository as ApiKeyRepository

__all__ = ["RoleRepository", "ApiKeyRepository"]

def init():
    from adh6.storage import session
    from .models import AuthenticationRoleMapping
    from ..config import Config
    from ..enums import AuthenticationMethod

    import logging

    logging.info(f"--- Setup OIDC default role mapping: {Config.DEFAULT_OIDC_AUTH_MAPPING} ---")
    for k in Config.DEFAULT_OIDC_AUTH_MAPPING:
        roles = Config.DEFAULT_OIDC_AUTH_MAPPING[k]
        for e in roles:
            v = session.query(AuthenticationRoleMapping)\
                .filter(AuthenticationRoleMapping.authentication == AuthenticationMethod.OIDC)\
                .filter(AuthenticationRoleMapping.identifier == k)\
                .filter(AuthenticationRoleMapping.role == e).one_or_none()
            if v is None:
                logging.warning(f"Role mapping not found creating it: {k} <-> {e}")
                session.add(AuthenticationRoleMapping(
                        identifier=k,
                        role=e,
                        authentication=AuthenticationMethod.OIDC
                    )
                )
        session.commit()