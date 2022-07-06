# coding=utf-8
from src.entity import Switch, AbstractSwitch
from src.interface_adapter.http_api.default import DefaultHandler
from src.plugins.network.use_cases.switch_manager import SwitchManager


class SwitchHandler(DefaultHandler):
    def __init__(self, switch_manager: SwitchManager):
        super().__init__(Switch, AbstractSwitch, switch_manager)
