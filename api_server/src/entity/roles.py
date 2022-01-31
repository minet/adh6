from enum import Enum

from src.entity.util.logic import Expression


class Roles(Expression, Enum):
    USER = "adh6_user"
    ADMIN = "adh6_admin"
    SUPERADMIN = "adh6_superadmin"
    TRESO = "adh6_treso"
    VLAN_PROD = "cluster-prod"
    VLAN_DEV = "cluster-dev"
    VLAN_HOSTING = "cluster-hosting"

    def __call__(self, arguments):
        roles = arguments['Roles']

        return self.value in roles
