import abc
import typing as t

class NotificationTemplate:
    def __init__(self, title: str, template: str) -> None:
        self.title = title
        self.template = template

class NotificationTemplateRepository(abc.ABC):
    @abc.abstractclassmethod
    def get(self, ctx, template_title: str) -> t.Union[NotificationTemplate, None]:
        pass # pragma: no cover

    @abc.abstractclassmethod
    def put(self, ctx, template: NotificationTemplate) -> int:
        pass # pragma: no cover