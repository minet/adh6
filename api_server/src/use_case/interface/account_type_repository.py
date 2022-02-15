# coding=utf-8
from src.use_case.interface.crud_repository import CRUDRepository
from src.entity import AccountType

class AccountTypeRepository(CRUDRepository[AccountType, AccountType]):
    pass
