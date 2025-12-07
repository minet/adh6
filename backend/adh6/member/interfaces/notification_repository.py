import abc


class NotificationRepository(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def send(cls, recipient: str, subject: str, body: str):
        pass  # pragma: no cover
