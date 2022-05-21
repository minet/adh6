import os
from typing import Any, Dict, List, Optional
from gitlab.client import Gitlab
from gitlab.exceptions import GitlabAuthenticationError

from src.util.log import logger


class BugReportManager:
    """
    Response to health requests.
    """

    def __init__(self):
        self.testing = os.environ.get('ENVIRONMENT', 'default').lower() == "testing"

        try:
            self.gl = Gitlab('https://gitlab.minet.net', private_token=os.environ.get("GITLAB_ACCESS_TOKEN"), api_version="4")
            self.gl.auth()
            self.project = self.gl.projects.get(223)
        except GitlabAuthenticationError:
            logger.error("Could not authenticate against MiNET's Gitlab server, bug reporting will not be available.")
            self.gl = None
            self.project = None

    def create(self, title: str = "", description: str = "", labels: Optional[List[str]] = None) -> Dict[str, Any]:
        if self.testing:
            return {
                "title": title,
                "description": description,
                "labels": labels,
                "web_url": ""
            }

        if self.gl is None or self.project is None:
            raise RuntimeError("Gitlab initialisation failed, bug reporting is unavailable.")

        if labels is None:
            labels = []

        return self.project.issues.create(
            {
                'title': title,
                'description': description,
                'labels': labels
            }
        ).attributes

