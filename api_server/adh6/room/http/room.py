# coding=utf-8
from adh6.entity import Room, AbstractRoom
from adh6.default.http_handler import DefaultHandler
from adh6.room.room_manager import RoomManager


class RoomHandler(DefaultHandler):
    def __init__(self, room_manager: RoomManager):
        super().__init__(Room, AbstractRoom, room_manager)
