from pipes import Template
from re import template
from adh6.decorator.log_call import log_call
from sqlalchemy.orm import Session
import typing as t
from sqlalchemy import select, insert
from adh6.constants import CTX_SQL_SESSION
from adh6.entity.member import Member

from ..interfaces.notification_template_repository import NotificationTemplateRepository, NotificationTemplate
from .models import NotificationTemplate as SQLNotificationTemplate


class NotificationTemplateSQLRepository(NotificationTemplateRepository):
    @log_call
    def get(self, ctx, template_title: str) -> t.Union[NotificationTemplate, None]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt = select(SQLNotificationTemplate).where(SQLNotificationTemplate.title == template_title)
        sql_template = session.execute(smt).one_or_none()
        return _map_template_to_sql_entity(sql_template[0]) if sql_template[0] else None

    @log_call
    def put(self, ctx, template: NotificationTemplate) -> int:
        session: Session = ctx.get(CTX_SQL_SESSION)
        smt = insert(SQLNotificationTemplate).values(
            title = template.title,
            template = template.template
        )
        print(session.execute(smt))
        return session.execute(select(SQLNotificationTemplate.id).where(SQLNotificationTemplate.title == template.title)).scalars

def _map_template_to_sql_entity(template: SQLNotificationTemplate) -> NotificationTemplate:
    return NotificationTemplate(
        title = template.title,
        template = template.template
    )