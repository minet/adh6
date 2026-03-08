from adh6.exceptions import MemberNotFoundError, ValidationError

from .interfaces import MailinglistRepository, MemberRepository


def _validate_mailinglist_value(value: int) -> None:
    """Validate that mailinglist value is between 0 and 255."""
    if not (0 <= value <= 255):
        raise ValidationError(
            f"Invalid mailinglist value: {value}. Must be between 0 and 255."
        )


class MailinglistManager:
    def __init__(
        self,
        member_repository: MemberRepository,
        mailinglist_repository: MailinglistRepository,
    ) -> None:
        self.member_repository = member_repository
        self.mailinglist_repository = mailinglist_repository

    async def get_member_mailinglist(self, member_id: int) -> int:
        m = await self.member_repository.get_by_id(member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        return await self.mailinglist_repository.get_from_member(member_id)

    async def update_member_mailinglist(self, member_id: int, value: int) -> None:
        _validate_mailinglist_value(value)
        m = await self.member_repository.get_by_id(member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        await self.mailinglist_repository.update_from_member(member_id, value)

    async def get_members(self, value: int) -> list[int]:
        _validate_mailinglist_value(value)
        return await self.mailinglist_repository.list_members(value)
