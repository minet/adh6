import abc
import datetime
import typing as t

class CharterRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, charter_id, member_id) -> t.Union[datetime.datetime, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_members(self, charter_id) -> t.Tuple[t.List[int], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update(self, charter_id, member_id) -> None:
        pass  # pragma: no cover
