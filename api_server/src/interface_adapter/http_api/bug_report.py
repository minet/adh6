# coding=utf-8

from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.util.error import handle_error
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.bug_report_manager import BugReportManager
from src.util.context import log_extra
from src.util.log import LOG


class BugReportHandler:
    def __init__(self, bug_report_manager: BugReportManager):
        self.bug_report_manager = bug_report_manager

    @with_context
    @require_sql
    def post(self, ctx, body):
        """ Add a new issue to the gitlab project """
        LOG.debug("http_bug_report_post_called", extra=log_extra(ctx, request=body))

        try:
            _ = self.bug_report_manager.create(title=body.get("title", ""), description=body.get("description", ""), labels=body.get("labels", None))
            return None, 204
        except Exception as e:
            return handle_error(ctx, e)

