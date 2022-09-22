import enum
import imp
from operator import xor
from pipes import Template
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.auto_raise import auto_raise
from adh6.constants import MembershipDuration
from adh6.member.interfaces.notification_repository import NotificationRepository
from adh6.member.interfaces.notification_template_repository import NotificationTemplateRepository
from adh6.exceptions import TemplateNotFoundError, UndecalredVariableInTemplate
from jinja2 import Template, Environment, meta
from jinja2.meta import find_undeclared_variables

class NotificationManager:
    def __init__(self, notification_repository: NotificationRepository, 
                notification_template_repository: NotificationTemplateRepository) -> None:
        self.notification_repository = notification_repository
        self.notification_template_repository = notification_template_repository

    @log_call
    @auto_raise
    def send(self, ctx, template_title: str, member_email: str, **kwargs):
        # check if template exist
        
        template = self.notification_template_repository.get(ctx, template_title)
        print(template)
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

        self.notification_repository.send(ctx, member_email, template_title, body)
