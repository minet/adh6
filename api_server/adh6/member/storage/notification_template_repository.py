from pipes import Template
from re import template
from adh6.decorator.log_call import log_call
import typing as t
from sqlalchemy import select, insert
from adh6.entity import Member
from adh6.storage import session

from ..interfaces.notification_template_repository import NotificationTemplateRepository, NotificationTemplate
from .models import NotificationTemplate as SQLNotificationTemplate


class NotificationTemplateSQLRepository(NotificationTemplateRepository):
    def get(self, template_title: str) -> t.Union[NotificationTemplate, None]:
        smt = select(SQLNotificationTemplate).where(SQLNotificationTemplate.title == template_title)
        sql_template = session.execute(smt).one_or_none()
        return _map_template_to_sql_entity(sql_template[0]) if sql_template[0] else None

    def put(self, template: NotificationTemplate) -> int:
        smt = insert(SQLNotificationTemplate).values(
            title = template.title,
            template = template.template
        )
        return session.execute(select(SQLNotificationTemplate.id).where(SQLNotificationTemplate.title == template.title)).scalars

def _map_template_to_sql_entity(template: SQLNotificationTemplate) -> NotificationTemplate:
    return NotificationTemplate(
        title = template.title,
        template = template.template
    )