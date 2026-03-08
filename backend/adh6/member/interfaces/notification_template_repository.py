import abc


class NotificationTemplate:
    async def __init__(self, title: str, template: str) -> None:
        self.title = title
        self.template = template


class NotificationTemplateRepository(abc.ABC):
    @abc.abstractmethod
    async def get(self, template_title: str) -> NotificationTemplate | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def put(self, template: NotificationTemplate) -> int:
        pass  # pragma: no cover
