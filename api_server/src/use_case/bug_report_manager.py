import gitlab
from gitlab.v4.objects import ProjectIssue
from gitlab.exceptions import GitlabAuthenticationError

from src.exceptions import MissingRequiredField
from src.util.log import logger


class BugReportManager:
    """
    Response to health requests.
    """

    def __init__(self, gitlab_conf, testing):
        self.testing = testing

        if not self.testing:
            try:
                self.gl = gitlab.Gitlab('https://gitlab.minet.net', private_token=gitlab_conf['access_token'])
                self.gl.auth()
                self.project = self.gl.projects.get(223)
            except GitlabAuthenticationError:
                logger.error("Could not authenticate against MiNET's Gitlab server, bug reporting will not be available.")
                self.gl = None
                self.project = None

    def create_issue(self, ctx, title="", description="", labels=None) -> ProjectIssue:
        if self.testing:
            return None

        if self.gl is None or self.project is None:
            raise RuntimeError("Gitlab initialisation failed, bug reporting is unavailable.")

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

        if self.gl is None or self.project is None:
            raise RuntimeError("Gitlab initialisation failed, bug reporting is unavailable.")

        return self.project.labels.list()
