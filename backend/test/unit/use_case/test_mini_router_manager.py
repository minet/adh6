from datetime import date
from unittest.mock import AsyncMock, MagicMock

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
from adh6.mini_router.interfaces import MiniRouterRepository
from adh6.mini_router.mini_router_manager import MiniRouterManager
from adh6.treasury.interfaces import PaymentMethodRepository
from pytest import fixture, raises


@fixture
def mini_router_repository():
    repository = MagicMock(spec=MiniRouterRepository)
    repository.is_taken = AsyncMock(return_value=False)
    return repository


@fixture
def member_repository():
    repository = MagicMock(spec=MemberRepository)
    repository.get_by_id = AsyncMock(return_value=MagicMock())
    return repository


@fixture
def payment_method_repository():
    repository = MagicMock(spec=PaymentMethodRepository)
    repository.get_by_id = AsyncMock(return_value=MagicMock())
    return repository


@fixture
def manager(mini_router_repository, member_repository, payment_method_repository):
    return MiniRouterManager(
        mini_router_repository=mini_router_repository,
        member_repository=member_repository,
        payment_method_repository=payment_method_repository,
    )


def make_mini_router(**kwargs) -> MiniRouter:
    values = {
        "id": 1,
        "hardwareMac": "94:83:c4:1c:01:6e",
        "mac": "00-00-36-00-01-15",
        "ip": "10.30.0.115",
        "model": "beryl_giga",
        "configState": "pimped",
    }
    values.update(kwargs)
    return MiniRouter(**values)


def make_loan(**kwargs) -> MiniRouterLoan:
    values = {
        "id": 10,
        "miniRouter": 1,
        "member": 42,
        "startedAt": date(2026, 9, 1),
        "depositAmount": 80,
        "depositStatus": "held",
    }
    values.update(kwargs)
    return MiniRouterLoan(**values)


class TestSearch:
    async def test_negative_limit(self, manager):
        with raises(IntMustBePositive):
            await manager.search(limit=-1)

    async def test_negative_offset(self, manager):
        with raises(IntMustBePositive):
            await manager.search(offset=-1)

    async def test_forwards_filters(self, manager, mini_router_repository):
        mini_router_repository.search_by = AsyncMock(return_value=([], 0))
        assert await manager.search(limit=5, offset=2, terms="beryl", loaned=True) == ([], 0)
        mini_router_repository.search_by.assert_awaited_once_with(
            limit=5, offset=2, terms="beryl", loaned=True, overdue=None
        )


class TestCreate:
    async def test_normalizes_addresses(self, manager, mini_router_repository):
        mini_router_repository.create = AsyncMock(side_effect=lambda m: m)
        created = await manager.create(make_mini_router())
        assert created.hardware_mac == "94:83:C4:1C:01:6E"
        assert created.mac == "00:00:36:00:01:15"
        assert created.ip == "10.30.0.115"

    async def test_empty_optional_addresses(self, manager, mini_router_repository):
        mini_router_repository.create = AsyncMock(side_effect=lambda m: m)
        created = await manager.create(make_mini_router(mac="", ip=""))
        assert created.mac is None
        assert created.ip is None

    async def test_invalid_hardware_mac(self, manager):
        with raises(InvalidMACAddress):
            await manager.create(make_mini_router(hardwareMac="not a mac"))

    async def test_invalid_ip(self, manager):
        with raises(InvalidIPv4):
            await manager.create(make_mini_router(ip="10.30.0.300"))

    async def test_duplicate(self, manager, mini_router_repository):
        mini_router_repository.is_taken = AsyncMock(side_effect=lambda field, value, exclude_id: field == "ip")
        with raises(MiniRouterAlreadyExists):
            await manager.create(make_mini_router())


class TestUpdate:
    async def test_not_found(self, manager, mini_router_repository):
        mini_router_repository.get_by_id = AsyncMock(return_value=None)
        with raises(MiniRouterNotFoundError):
            await manager.update(1, make_mini_router())

    async def test_excludes_itself_from_uniqueness(self, manager, mini_router_repository):
        mini_router_repository.get_by_id = AsyncMock(return_value=make_mini_router())
        mini_router_repository.update = AsyncMock(side_effect=lambda id, m: m)
        await manager.update(1, make_mini_router())
        for call in mini_router_repository.is_taken.await_args_list:
            assert call.args[2] == 1


class TestDelete:
    async def test_not_found(self, manager, mini_router_repository):
        mini_router_repository.get_by_id = AsyncMock(return_value=None)
        with raises(MiniRouterNotFoundError):
            await manager.delete(1)

    async def test_blocked_by_loan_in_progress(self, manager, mini_router_repository):
        mini_router_repository.get_by_id = AsyncMock(return_value=make_mini_router())
        mini_router_repository.list_loans = AsyncMock(return_value=[make_loan(depositStatus="refunded")])
        with raises(MiniRouterDeletionBlocked):
            await manager.delete(1)

    async def test_blocked_by_held_deposit(self, manager, mini_router_repository):
        mini_router_repository.get_by_id = AsyncMock(return_value=make_mini_router())
        mini_router_repository.list_loans = AsyncMock(return_value=[make_loan(returnedAt=date(2026, 9, 10))])
        with raises(MiniRouterDeletionBlocked):
            await manager.delete(1)

    async def test_deletes_with_settled_history(self, manager, mini_router_repository):
        mini_router_repository.get_by_id = AsyncMock(return_value=make_mini_router())
        mini_router_repository.list_loans = AsyncMock(
            return_value=[make_loan(returnedAt=date(2026, 9, 10), depositStatus="kept")]
        )
        mini_router_repository.delete = AsyncMock()
        await manager.delete(1)
        mini_router_repository.delete.assert_awaited_once_with(1)


class TestListLoans:
    async def test_not_found(self, manager, mini_router_repository):
        mini_router_repository.get_by_id = AsyncMock(return_value=None)
        with raises(MiniRouterNotFoundError):
            await manager.list_loans(1)

    async def test_member_loans(self, manager, mini_router_repository):
        mini_router_repository.list_loans = AsyncMock(return_value=[make_loan()])
        assert await manager.list_member_loans(42) == [make_loan()]
        mini_router_repository.list_loans.assert_awaited_once_with(member_id=42)


class TestCreateLoan:
    async def test_already_loaned(self, manager, mini_router_repository):
        mini_router_repository.get_by_id = AsyncMock(return_value=make_mini_router(currentLoan=make_loan()))
        with raises(MiniRouterAlreadyLoaned):
            await manager.create_loan(1, make_loan(), 7)

    async def test_member_not_found(self, manager, mini_router_repository, member_repository):
        mini_router_repository.get_by_id = AsyncMock(return_value=make_mini_router())
        member_repository.get_by_id = AsyncMock(return_value=None)
        with raises(MemberNotFoundError):
            await manager.create_loan(1, make_loan(), 7)

    async def test_payment_method_not_found(self, manager, mini_router_repository, payment_method_repository):
        mini_router_repository.get_by_id = AsyncMock(return_value=make_mini_router())
        payment_method_repository.get_by_id = AsyncMock(return_value=None)
        with raises(PaymentMethodNotFoundError):
            await manager.create_loan(1, make_loan(paymentMethod=3), 7)

    async def test_invalid_dates(self, manager, mini_router_repository):
        mini_router_repository.get_by_id = AsyncMock(return_value=make_mini_router())
        with raises(InvalidLoanDates):
            await manager.create_loan(1, make_loan(returnedAt=date(2026, 8, 1)), 7)

    async def test_creates(self, manager, mini_router_repository):
        loan = make_loan(paymentMethod=1)
        mini_router_repository.get_by_id = AsyncMock(return_value=make_mini_router())
        mini_router_repository.create_loan = AsyncMock(return_value=loan)
        assert await manager.create_loan(1, loan, 7) == loan
        mini_router_repository.create_loan.assert_awaited_once_with(1, loan, 7)

    async def test_deposit_is_always_held(self, manager, mini_router_repository):
        mini_router_repository.get_by_id = AsyncMock(return_value=make_mini_router())
        mini_router_repository.create_loan = AsyncMock(side_effect=lambda id, loan, author_id: loan)
        created = await manager.create_loan(1, make_loan(depositStatus="refunded"), 7)
        assert created.deposit_status == "held"


class TestUpdateLoan:
    async def test_not_found(self, manager, mini_router_repository):
        mini_router_repository.get_loan = AsyncMock(return_value=None)
        with raises(MiniRouterLoanNotFoundError):
            await manager.update_loan(10, make_loan())

    async def test_member_cannot_change(self, manager, mini_router_repository):
        mini_router_repository.get_loan = AsyncMock(return_value=make_loan())
        with raises(UpdateImpossible):
            await manager.update_loan(10, make_loan(member=7))

    async def test_reopen_blocked_by_other_loan(self, manager, mini_router_repository):
        mini_router_repository.get_loan = AsyncMock(return_value=make_loan(returnedAt=date(2026, 9, 10)))
        mini_router_repository.get_by_id = AsyncMock(return_value=make_mini_router(currentLoan=make_loan(id=11)))
        with raises(MiniRouterAlreadyLoaned):
            await manager.update_loan(10, make_loan())

    async def test_keeps_deposit_status_when_missing(self, manager, mini_router_repository):
        mini_router_repository.get_loan = AsyncMock(return_value=make_loan(depositStatus="kept"))
        mini_router_repository.update_loan = AsyncMock(side_effect=lambda id, loan: loan)
        updated = await manager.update_loan(10, MiniRouterLoan(member=42, startedAt=date(2026, 9, 1), depositAmount=80))
        assert updated.deposit_status == "kept"

    async def test_returns_loan(self, manager, mini_router_repository):
        returned = make_loan(returnedAt=date(2026, 9, 10), depositStatus="refunded")
        mini_router_repository.get_loan = AsyncMock(return_value=make_loan())
        mini_router_repository.update_loan = AsyncMock(return_value=returned)
        assert await manager.update_loan(10, returned) == returned
