# coding=utf-8

import abc
import ipaddress
import typing as t

from adh6.entity import Member, AbstractMember, MemberFilter
from adh6.default import CRUDRepository


class MemberRepository(CRUDRepository[Member, AbstractMember]):
    @abc.abstractmethod
    def search_by(self, limit: int, offset: int, terms: t.Optional[str] = None, filter_: t.Optional[MemberFilter] = None) -> t.Tuple[t.List[Member], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_by_id(self, object_id: int) -> t.Union[Member, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_by_login(self, login: str) -> t.Union[Member, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def add_duration(self, member_id: int, duration_in_mounth: int) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_password(self, member_id: int, hashed_password: str) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def used_wireless_public_ips(self) -> t.List[ipaddress.IPv4Address]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_comment(self, member_id: int, comment: str) -> None:
        pass  # pragma: no cover