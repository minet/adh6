from adh6.default.http_handler import DefaultHandler
from adh6.entity import AbstractSwitch, Switch

from ..switch_manager import SwitchManager


class SwitchHandler(DefaultHandler):
    def __init__(self, switch_manager: SwitchManager):
        super().__init__(Switch, AbstractSwitch, switch_manager)
