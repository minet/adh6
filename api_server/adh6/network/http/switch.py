# coding=utf-8
from adh6.entity import Switch, AbstractSwitch
from adh6.default.http_handler import DefaultHandler

from ..switch_manager import SwitchManager


class SwitchHandler(DefaultHandler):
    def __init__(self, switch_manager: SwitchManager):
        super().__init__(Switch, AbstractSwitch, switch_manager)
