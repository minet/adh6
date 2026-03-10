import abc


class PingRepository(abc.ABC):
    """
    Abstract interface to get the health of the DB.
    """

    @abc.abstractmethod
    async def ping(self) -> bool:
        pass  # pragma: no cover
