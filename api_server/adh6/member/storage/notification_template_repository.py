from sqlalchemy import select

from adh6.storage import db

from ..interfaces.notification_template_repository import NotificationTemplate, NotificationTemplateRepository
from .models import NotificationTemplate as SQLNotificationTemplate


class NotificationTemplateSQLRepository(NotificationTemplateRepository):
    def get(self, template_title: str) -> NotificationTemplate | None:
        smt = select(SQLNotificationTemplate).where(SQLNotificationTemplate.title == template_title)
        sql_template = db.session.execute(smt).one()
        return _map_template_to_sql_entity(sql_template[0]) if sql_template[0] else None

    def put(self, template: NotificationTemplate) -> int:
        # TODO: I think something is broken here. Did notification already worked ?
        # smt = insert(SQLNotificationTemplate).values(title=template.title, template=template.template)
        return db.session.execute(
            select(SQLNotificationTemplate.id).where(SQLNotificationTemplate.title == template.title)
        ).scalar_one()


def _map_template_to_sql_entity(template: SQLNotificationTemplate) -> NotificationTemplate:
    return NotificationTemplate(title=template.title, template=template.template)  #  type: ignore  # TODO: understand what is a template and fix typing
