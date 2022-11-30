from pipes import Template
from adh6.decorator import log_call
from adh6.exceptions import TemplateNotFoundError, UndecalredVariableInTemplate
from jinja2 import Template, Environment, meta

from .interfaces import NotificationRepository, NotificationTemplateRepository


class NotificationManager:
    def __init__(self, notification_repository: NotificationRepository, 
                notification_template_repository: NotificationTemplateRepository) -> None:
        self.notification_repository = notification_repository
        self.notification_template_repository = notification_template_repository

    @log_call
    def send(self, template_title: str, member_email: str, **kwargs):
        # check if template exist
        
        template = self.notification_template_repository.get(template_title)
        if not template:
                raise TemplateNotFoundError(template_title)

        # TODO: Check exactly all args for the template, no more, no less
        env = Environment()
        template_parsed = env.parse(template.template)
        variables_in_template = set(meta.find_undeclared_variables(template_parsed))
        variables_in_parameter = set(kwargs.keys())
        if len(variables_in_template) != len(variables_in_parameter):
                raise UndecalredVariableInTemplate(variables_in_template^variables_in_parameter)
        template = Template(template.template)
        body = template.render(**kwargs)

        self.notification_repository.send(member_email, template_title, body)
