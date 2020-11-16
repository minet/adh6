from enum import Enum

from src.entity.util.logic import Expression


class Roles(Expression, Enum):
    ADH6_USER = "adh6_user"
    ADH6_ADMIN = "adh6_admin"
    ADH6_SUPER_ADMIN = "adh6_super_admin"
    ADH6_TRESO = "adh6_treso"

    def __call__(self, arguments):
        roles = arguments['Roles']

        return self.value in roles
