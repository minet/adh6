import abc
import typing as t

class MailinglistRepository(abc.ABC):
    @abc.abstractmethod
    def list_members(self, value: int) -> t.List[int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_from_member(self, member_id: int) -> int:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_from_member(self, member_id: int, value: int) -> None:
        pass  # pragma: no cover
