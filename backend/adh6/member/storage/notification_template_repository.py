from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..interfaces.notification_template_repository import NotificationTemplate, NotificationTemplateRepository
from .models import NotificationTemplate as SQLNotificationTemplate


class NotificationTemplateSQLRepository(NotificationTemplateRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, template_title: str) -> NotificationTemplate | None:
        smt = select(SQLNotificationTemplate).where(SQLNotificationTemplate.title == template_title)
        result = await self.session.execute(smt)
        sql_template = result.one()
        return _map_template_to_sql_entity(sql_template[0]) if sql_template[0] else None

    async def put(self, template: NotificationTemplate) -> int:
        # TODO: I think something is broken here. Did notification already worked ?
        # smt = insert(SQLNotificationTemplate).values(title=template.title, template=template.template)
        result = await self.session.execute(
            select(SQLNotificationTemplate.id).where(SQLNotificationTemplate.title == template.title)
        )
        return result.scalar_one()


def _map_template_to_sql_entity(template: SQLNotificationTemplate) -> NotificationTemplate:
    return NotificationTemplate(title=template.title, template=template.template)  #  type: ignore  # TODO: understand what is a template and fix typing
