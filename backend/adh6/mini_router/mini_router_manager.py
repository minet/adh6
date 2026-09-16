from ipaddress import AddressValueError, IPv4Address

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.decorator import log_call
from adh6.entity import MiniRouter, MiniRouterLoan
from adh6.exceptions import (
    IntMustBePositive,
    InvalidIPv4,
    InvalidLoanDates,
    InvalidMACAddress,
    MemberNotFoundError,
    MiniRouterAlreadyExists,
    MiniRouterAlreadyLoaned,
    MiniRouterDeletionBlocked,
    MiniRouterLoanNotFoundError,
    MiniRouterNotFoundError,
    PaymentMethodNotFoundError,
    UpdateImpossible,
)
from adh6.member.interfaces.member_repository import MemberRepository
from adh6.misc.validator import is_mac_address
from adh6.treasury.interfaces import PaymentMethodRepository

from .interfaces import MiniRouterRepository

DEPOSIT_HELD = "held"


def normalize_mac(value: str) -> str:
    if not is_mac_address(value):
        raise InvalidMACAddress(value)
    return value.upper().replace("-", ":")


def normalize_ip(value: str) -> str:
    try:
        return str(IPv4Address(value))
    except AddressValueError as e:
        raise InvalidIPv4(value) from e


class MiniRouterManager:
    """
    Implements all the use cases related to mini-router and loan management.
    """

    def __init__(
        self,
        mini_router_repository: MiniRouterRepository,
        member_repository: MemberRepository,
        payment_method_repository: PaymentMethodRepository,
    ):
        self.mini_router_repository = mini_router_repository
        self.member_repository = member_repository
        self.payment_method_repository = payment_method_repository

    @log_call
    async def search(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        terms: str | None = None,
        loaned: bool | None = None,
        overdue: bool | None = None,
    ) -> tuple[list[MiniRouter], int]:
        if limit < 0:
            raise IntMustBePositive("limit")
        if offset < 0:
            raise IntMustBePositive("offset")
        return await self.mini_router_repository.search_by(
            limit=limit, offset=offset, terms=terms, loaned=loaned, overdue=overdue
        )

    @log_call
    async def get_by_id(self, id: int) -> MiniRouter:
        mini_router = await self.mini_router_repository.get_by_id(id)
        if mini_router is None:
            raise MiniRouterNotFoundError(id)
        return mini_router

    @log_call
    async def create(self, mini_router: MiniRouter) -> MiniRouter:
        await self._validate(mini_router)
        return await self.mini_router_repository.create(mini_router)

    @log_call
    async def update(self, id: int, mini_router: MiniRouter) -> MiniRouter:
        await self.get_by_id(id)
        await self._validate(mini_router, exclude_id=id)
        return await self.mini_router_repository.update(id, mini_router)

    @log_call
    async def delete(self, id: int) -> None:
        await self.get_by_id(id)
        loans = await self.mini_router_repository.list_loans(mini_router_id=id)
        if any(loan.returned_at is None or loan.deposit_status == DEPOSIT_HELD for loan in loans):
            raise MiniRouterDeletionBlocked(id)
        await self.mini_router_repository.delete(id)

    @log_call
    async def list_loans(self, id: int) -> list[MiniRouterLoan]:
        await self.get_by_id(id)
        return await self.mini_router_repository.list_loans(mini_router_id=id)

    @log_call
    async def list_member_loans(self, member_id: int) -> list[MiniRouterLoan]:
        return await self.mini_router_repository.list_loans(member_id=member_id)

    @log_call
    async def create_loan(self, id: int, loan: MiniRouterLoan, author_id: int) -> MiniRouterLoan:
        mini_router = await self.get_by_id(id)
        if mini_router.current_loan is not None:
            raise MiniRouterAlreadyLoaned(id)
        if loan.member is None or await self.member_repository.get_by_id(loan.member) is None:
            raise MemberNotFoundError(loan.member)
        await self._validate_loan(loan)
        loan.deposit_status = DEPOSIT_HELD
        return await self.mini_router_repository.create_loan(id, loan, author_id)

    @log_call
    async def update_loan(self, loan_id: int, loan: MiniRouterLoan) -> MiniRouterLoan:
        existing = await self.mini_router_repository.get_loan(loan_id)
        if existing is None or existing.mini_router is None:
            raise MiniRouterLoanNotFoundError(loan_id)
        if loan.member is not None and loan.member != existing.member:
            raise UpdateImpossible("mini_router_loan", "the member of a loan cannot be changed")
        if existing.returned_at is not None and loan.returned_at is None:
            mini_router = await self.get_by_id(existing.mini_router)
            if mini_router.current_loan is not None:
                raise MiniRouterAlreadyLoaned(existing.mini_router)
        await self._validate_loan(loan)
        if loan.deposit_status is None:
            loan.deposit_status = existing.deposit_status
        return await self.mini_router_repository.update_loan(loan_id, loan)

    async def _validate(self, mini_router: MiniRouter, exclude_id: int | None = None) -> None:
        """Normalize the addresses in place and check they are not used by another mini-router."""
        mini_router.hardware_mac = normalize_mac(mini_router.hardware_mac)
        mini_router.mac = normalize_mac(mini_router.mac) if mini_router.mac else None
        mini_router.ip = normalize_ip(mini_router.ip) if mini_router.ip else None

        for field in ("hardware_mac", "mac", "ip"):
            value = getattr(mini_router, field)
            if value and await self.mini_router_repository.is_taken(field, value, exclude_id):
                raise MiniRouterAlreadyExists(field, value)

    async def _validate_loan(self, loan: MiniRouterLoan) -> None:
        if loan.returned_at is not None and loan.started_at is not None and loan.returned_at < loan.started_at:
            raise InvalidLoanDates
        if (
            loan.payment_method is not None
            and await self.payment_method_repository.get_by_id(loan.payment_method) is None
        ):
            raise PaymentMethodNotFoundError(loan.payment_method)
