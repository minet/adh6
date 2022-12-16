import abc
import datetime
import typing as t

class CharterRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, charter_id: int, member_id: int) -> t.Union[datetime.datetime, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_members(self, charter_id: int) -> t.Tuple[t.List[int], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update(self, charter_id: int, member_id: int) -> None:
        pass  # pragma: no cover
