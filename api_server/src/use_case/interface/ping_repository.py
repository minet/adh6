import abc


class PingRepository(abc.ABC):
    """
    Abstract interface to get the health of the DB.
    """

    @abc.abstractmethod
    def ping(self, ctx) -> bool:
        pass  # pragma: no cover
