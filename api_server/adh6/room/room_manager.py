# coding=utf-8
import typing as t

from adh6.decorator import log_call
from adh6.exceptions import RoomNotFoundError
from adh6.default import CRUDManager
from adh6.member import MemberManager
from adh6.entity import Room

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
    def get_by_number(self, room_number: int) -> Room:
        r = self.room_repository.get_by_number(room_number)
        if not r:
            raise RoomNotFoundError(room_number)
        return r

    @log_call
    def add_member(self, room_number: int, login: str) -> None:
        room = self.get_by_number(room_number)
        member = self.member_manager.get_by_login(login)
        
        previous_room = self.room_repository.get_from_member(member)
        if previous_room:
            self.room_repository.remove_member(member)

        self.room_repository.add_member(room.id, member)
        if not previous_room:
            self.member_manager.update_subnet(member_id=member.id)
            self.member_manager.ethernet_vlan_changed(member.id, room.vlan)
        elif previous_room.vlan != room.vlan:
            self.member_manager.ethernet_vlan_changed(member.id, room.vlan)

    @log_call
    def remove_member(self, login: str) -> None:
        member = self.member_manager.get_by_login(login)
        self.room_repository.remove_member(member)
        self.member_manager.reset_member(member.id)

    @log_call
    def list_members(self, room_number: int) -> t.List[str]:
        room = self.get_by_number(room_number)
        return self.room_repository.get_members(room_id=room.id)

    @log_call
    def room_from_member(self, login: str) -> Room:
        member = self.member_manager.get_by_login(login)
        room = self.room_repository.get_from_member(member)
        if not room:
            raise RoomNotFoundError()
        return room
