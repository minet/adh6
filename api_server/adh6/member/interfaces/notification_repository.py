import abc

class NotificationRepository(abc.ABC):
    @abc.abstractclassmethod
    def send(self, recipient: str, subject: str, body: str):
        pass # pragma: no cover