# coding=utf-8
from src.entity import Room, AbstractRoom
from src.interface_adapter.http_api.default import DefaultHandler
from src.use_case.room_manager import RoomManager


class RoomHandler(DefaultHandler):
    def __init__(self, room_manager: RoomManager):
        super().__init__(Room, AbstractRoom, room_manager)
