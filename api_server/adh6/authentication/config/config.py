import typing as t

from ..enums import Roles


class Config:
    DEFAULT_OIDC_AUTH_MAPPING: t.Dict[str, t.List[Roles]] = {
        "adh6_admin": [Roles.ADMIN_READ, Roles.ADMIN_WRITE, Roles.NETWORK_READ, Roles.NETWORK_WRITE, Roles.ADMIN_PROD],
        "adh6_treso": [Roles.TRESO_READ, Roles.TRESO_WRITE]
    }