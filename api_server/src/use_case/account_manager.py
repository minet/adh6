from dataclasses import asdict
from typing import List

from src.constants import DEFAULT_OFFSET, DEFAULT_LIMIT
from src.entity import AbstractAccount
from src.entity.account import Account
from src.exceptions import AccountNotFoundError, IntMustBePositive, StringMustNotBeEmpty, MissingRequiredField
from src.use_case.base_manager import BaseManager
from src.use_case.interface.account_repository import AccountRepository
from src.use_case.interface.member_repository import MemberRepository
from src.util.context import log_extra
from src.util.log import LOG


class AccountManager(BaseManager):
    def __init__(self, member_repository: MemberRepository, account_repository: AccountRepository):
        self.account_repository = account_repository
        self.member_repository = member_repository

    def get_by_id(self, ctx, account_id=None, **kwargs) -> Account:
        """
        Search an account in the database.
        """

        result, count = self.account_repository.search_account_by(ctx, account_id=account_id)

        if count == 0:
            raise AccountNotFoundError

        # TODO: LOG.info

        return result[0]

    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, account_id=None, terms=None, pinned=None) -> (
            List[Account], int):
        """
        search member in the database.

        user story: as an admin, i want to have a list of accounts with some filters, so that i can browse and find
        accounts.

        :raise intmustbepositiveexception
        """
        if limit < 0:
            raise IntMustBePositive('limit')

        if offset < 0:
            raise IntMustBePositive('offset')

        result, count = self.account_repository.search_account_by(ctx,
                                                                  limit=limit,
                                                                  offset=offset,
                                                                  account_id=account_id,
                                                                  pinned=None,
                                                                  terms=terms)

        # Log action.
        LOG.info('account_search', extra=log_extra(
            ctx,
            account_id=account_id,
            terms=terms,
        ))
        return result, count

    def update_or_create(self, ctx, req: AbstractAccount, account_id=None) -> bool:
        req.validate()

        try:
            result, _ = self.account_repository.search_account_by(ctx, account_id=account_id)
            fields = {k: v for k, v in asdict(req).items()}

        except AccountNotFoundError:
            raise
        if req.name == '':
            raise StringMustNotBeEmpty('name')
        if not req.name:
            raise MissingRequiredField('name')
        if not req.type:
            raise MissingRequiredField('type')

        if not result or not account_id:
            LOG.info('account_create', extra=log_extra(
                ctx,
                account_id=account_id,
                type=req.type
            ))
            # No account with that name, creating one...
            self.account_repository.create_account(ctx, **fields)
            return True

        else:
            # An account exists, updating it
            # Warning: AccountNotFound
            LOG.info('account_update', extra=log_extra(
                ctx,
                account_id=account_id,
            ))
            self.account_repository.update_account(ctx, account_id=account_id, **fields)
            return False

    def get_cav_balance(self, ctx):
        results, count = self.account_repository.search_account_by(ctx, compte_courant=True)
        return sum(list(map(lambda a: a.balance, results)))

