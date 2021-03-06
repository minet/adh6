# coding=utf-8

from typing import List

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import Member, AbstractMember
from src.use_case.interface.crud_repository import CRUDRepository


class MemberRepository(CRUDRepository):
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractMember = None) -> (List[Member], int):
        raise NotImplemented

    def create(self, ctx, object_to_create: Member) -> object:
        raise NotImplemented

    def update(self, ctx, object_to_update: AbstractMember, override=False) -> object:
        raise NotImplemented

    def delete(self, ctx, object_id) -> None:
        raise NotImplemented

    def update_password(self, ctx, member_id, hashed_password):
        raise NotImplemented
