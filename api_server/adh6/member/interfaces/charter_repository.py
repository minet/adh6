import abc
from datetime import datetime
from typing import List, Tuple, Union

class CharterRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, charter_id, member_id) -> Union[datetime, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_members(self, charter_id) -> Tuple[List[int], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update(self, charter_id, member_id) -> None:
        pass  # pragma: no cover
