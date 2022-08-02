from typing import List
import abc

class MailinglistRepository(abc.ABC):
    @abc.abstractmethod
    def list_members(self, ctx, value: int) -> List[int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_from_member(self, ctx, member_id: int) -> int:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_from_member(self, ctx, member_id: int, value: int) -> None:
        pass  # pragma: no cover
