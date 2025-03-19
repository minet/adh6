# coding=utf-8

import abc
import ipaddress
from typing import List, Tuple

from adh6.default.crud_repository import CRUDRepository
from adh6.entity import AbstractMember, Member, MemberFilter


class MemberRepository(CRUDRepository[Member, AbstractMember]):
    @abc.abstractmethod
    def search_by(
        self, limit: int, offset: int, terms: str | None = None, filter_: MemberFilter | None = None
    ) -> Tuple[List[Member], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_by_id(self, object_id: int) -> Member | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_by_login(self, login: str) -> Member | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def add_duration(self, member_id: int, duration_in_mounth: int) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_password(self, member_id: int, hashed_password: str) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def used_wireless_public_ips(self) -> List[ipaddress.IPv4Address]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_comment(self, member_id: int, comment: str) -> None:
        pass  # pragma: no cover
