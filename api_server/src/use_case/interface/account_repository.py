# coding=utf-8

import abc
from typing import Optional

from src.entity import Account, AbstractAccount
from src.use_case.interface.crud_repository import CRUDRepository


class AccountRepository(CRUDRepository[Account, AbstractAccount]):
    @abc.abstractmethod
    def get(self, ctx, id: int) -> Optional[Account]:
        pass
