import gitlab
from gitlab.v4.objects import ProjectIssue

from src.exceptions import MissingRequiredField


class BugReportManager:
    """
    Response to health requests.
    """

    def __init__(self, gitlab_conf, testing):
        self.testing = testing

        if not self.testing:
            self.gl = gitlab.Gitlab('https://gitlab.minet.net', private_token=gitlab_conf['access_token'])
            self.gl.auth()
            self.project = self.gl.projects.get(223)

    def create_issue(self, ctx, title="", description="", labels=None) -> ProjectIssue:
        if self.testing:
            return None

        if labels is None:
            labels = []
        if not title:
            raise MissingRequiredField("title")
        if not description:
            raise MissingRequiredField("description")

        return self.project.issues.create({'title': title,
                                           'description': description,
                                           'labels': labels})

    def get_labels(self, ctx) -> list:
        if self.testing:
            return []
        return self.project.labels.list()
