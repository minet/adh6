# coding=utf-8

import abc
import ipaddress
from typing import List
from src.entity import Member, AbstractMember
from src.use_case.interface.crud_repository import CRUDRepository


class MemberRepository(CRUDRepository[Member, AbstractMember]):
    @abc.abstractmethod
    def add_duration(self, ctx, member_id: int, duration_in_mounth: int) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_password(self, ctx, member_id: int, hashed_password: str) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_mailinglist(self, ctx, member_id: int, value: int) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_charter(self, ctx, member_id: int, charter_id: int) -> str:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_charter(self, ctx, member_id: int, charter_id: int) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def used_wireless_public_ips(self, ctx) -> List[ipaddress.IPv4Address]:
        pass  # pragma: no cover
