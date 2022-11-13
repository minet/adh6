# coding=utf-8

import abc
import ipaddress
from typing import List, Optional, Tuple, Union
from adh6.entity import Member, AbstractMember, MemberFilter
from adh6.default.crud_repository import CRUDRepository


class MemberRepository(CRUDRepository[Member, AbstractMember]):
    @abc.abstractmethod
    def search_by(self, ctx, limit: int, offset: int, terms: Optional[str] = None, filter_: Optional[MemberFilter] = None) -> Tuple[List[Member], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_by_id(self, ctx, object_id: int) -> Union[Member, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_by_login(self, ctx, login: str) -> Union[Member, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def add_duration(self, ctx, member_id: int, duration_in_mounth: int) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_password(self, ctx, member_id: int, hashed_password: str) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def used_wireless_public_ips(self, ctx) -> List[ipaddress.IPv4Address]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_comment(self, ctx, member_id: int, comment: str) -> None:
        pass  # pragma: no cover