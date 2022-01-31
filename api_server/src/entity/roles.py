from enum import Enum

from src.entity.util.logic import Expression


class Roles(Expression, Enum):
    ADH6_USER = "adh6_user"
    ADH6_ADMIN = "adh6_admin"
    ADH6_SUPERADMIN = "adh6_superadmin"
    ADH6_TRESO = "adh6_treso"
    ADH6_VLAN_PROD = "cluster-prod"
    ADH6_VLAN_DEV = "cluster-dev"
    ADH6_VLAN_HOSTING = "cluster-hosting"

    def __call__(self, arguments):
        roles = arguments['Roles']

        return self.value in roles
