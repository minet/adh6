# coding=utf-8

from gitlab.v4.objects import ProjectIssue

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
            issue = self.bug_report_manager.create_issue(ctx, title=body.get("title"), description=body.get("description"),
                                                         labels=body.get("labels"))
            return _map_project_issue_to_http_response(issue), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    def get_labels(self, ctx):
        """ List available labels from the gitlab project """
        LOG.debug("http_bug_report_get_labels_called", extra=log_extra(ctx))

        labels = self.bug_report_manager.get_labels(ctx)

        return {'labels': [label.name for label in labels]}, 200


def _map_project_issue_to_http_response(issue: ProjectIssue) -> dict:
    fields = {
        "title": issue.title,
        "description": issue.description,
        "labels": issue.labels,
        "link": issue.web_url
    }

    return {k: v for k, v in fields.items() if v is not None}
