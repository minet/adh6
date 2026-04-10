import abc


class MailinglistRepository(abc.ABC):
    @abc.abstractmethod
    async def list_members(self, value: int) -> list[int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def get_from_member(self, member_id: int) -> int:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def update_from_member(self, member_id: int, value: int) -> None:
        pass  # pragma: no cover
