# coding=utf-8
import typing as t

from adh6.decorator import log_call
from adh6.exceptions import NotFoundError, RoomNotFoundError
from adh6.default import CRUDManager
from adh6.member import MemberManager

from .interfaces import RoomRepository


class RoomManager(CRUDManager):
    """
    Implements all the use cases related to room management.
    """

    def __init__(self, room_repository: RoomRepository, member_manager: MemberManager):
        super().__init__(room_repository, RoomNotFoundError)
        self.room_repository = room_repository
        self.member_manager = member_manager

    @log_call
    def add_member(self, room_id: int, member_id: int) -> None:
        try:
            room = self.room_repository.get_by_id(room_id)
            if not room:
                raise RoomNotFoundError(room_id)
            self.member_manager.get_by_id(member_id)
        except NotFoundError as e:
            raise e
        
        previous_room = self.room_repository.get_from_member(member_id)
        if previous_room:
            self.room_repository.remove_member(member_id)

        self.room_repository.add_member(room_id, member_id)
        if not previous_room:
            self.member_manager.update_subnet(member_id=member_id)
            self.member_manager.ethernet_vlan_changed(member_id, room.vlan)
        elif previous_room.vlan != room.vlan:
            self.member_manager.ethernet_vlan_changed(member_id, room.vlan)

    @log_call
    def remove_member(self, room_id: int, member_id: int) -> None:
        try:
            self.member_manager.get_by_id(member_id)
            room = self.room_repository.get_by_id(room_id)
            if not room:
                raise RoomNotFoundError(room_id)
        except NotFoundError as e:
            raise e
        self.room_repository.remove_member(member_id)
        self.member_manager.reset_member(member_id)

    @log_call
    def list_members(self, room_id: int) -> t.List[int]:
        try:
            room = self.room_repository.get_by_id(room_id)
            if not room:
                raise RoomNotFoundError(room_id)
        except Exception as e:
            raise e
        return self.room_repository.get_members(room_id=room_id)

    @log_call
    def room_from_member(self, member_id: int) -> int:
        room = self.room_repository.get_from_member(member_id)
        if not room:
            raise RoomNotFoundError()
        return room.id
