# coding=utf-8

from typing import List
from adh6.default.decorator.log_call import log_call
from adh6.entity import AbstractRoom
from adh6.exceptions import NotFoundError, RoomNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.member.member_manager import MemberManager
from adh6.room.interfaces.room_repository import RoomRepository


class RoomManager(CRUDManager):
    """
    Implements all the use cases related to room management.
    """

    def __init__(self, room_repository: RoomRepository, member_manager: MemberManager):
        super().__init__(room_repository, AbstractRoom, RoomNotFoundError)
        self.room_repository = room_repository
        self.member_manager = member_manager

    @log_call
    def add_member(self, ctx, room_id: int, member_id: int) -> None:
        try:
            room = self.room_repository.get_by_id(ctx, room_id)
            self.member_manager.get_by_id(ctx, member_id)
        except NotFoundError as e:
            raise e
        
        previous_room = self.room_repository.get_from_member(ctx, member_id)
        if previous_room:
            self.room_repository.remove_member(ctx, room_id, member_id)

        print(previous_room)
        self.room_repository.add_member(ctx, room_id, member_id)
        if previous_room and previous_room.vlan != room.vlan:
            self.member_manager.ethernet_vlan_changed(ctx, member_id, room.vlan)

    @log_call
    def remove_member(self, ctx, room_id: int, member_id: int) -> None:
        try:
            self.member_manager.get_by_id(ctx, member_id)
            room = self.room_repository.get_by_id(ctx, room_id)
            if not room:
                raise RoomNotFoundError(room_id)
        except NotFoundError as e:
            raise e
        self.room_repository.remove_member(ctx, member_id)
        self.member_manager.reset_member(ctx, member_id)

    @log_call
    def list_members(self, ctx, room_id: int) -> List[int]:
        try:
            room = self.room_repository.get_by_id(ctx, room_id)
            if not room:
                raise RoomNotFoundError(room_id)
        except Exception as e:
            raise e
        return self.room_repository.get_members(ctx, room_id=room_id)

    @log_call
    def room_from_member(self, ctx, member_id: int) -> int:
        room = self.room_repository.get_from_member(ctx, member_id)
        if not room:
            raise RoomNotFoundError()
        return room.id
