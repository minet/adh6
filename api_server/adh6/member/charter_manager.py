from datetime import datetime
from typing import List, Tuple, Union
from adh6.exceptions import MemberNotFoundError
from adh6.member.interfaces.charter_repository import CharterRepository
from adh6.member.interfaces.member_repository import MemberRepository


class CharterManager:
    def __init__(self, charter_repository: CharterRepository, member_repository: MemberRepository) -> None:
        self.charter_repository = charter_repository
        self.member_repository = member_repository

    def get(self, ctx, charter_id: int, member_id: int) -> Union[datetime, None]:
        m = self.member_repository.get_by_id(ctx, member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        return self.charter_repository.get(ctx, charter_id, member_id)

    def sign(self, ctx, charter_id: int, member_id: int):
        m = self.member_repository.get_by_id(ctx, member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        self.charter_repository.update(ctx, charter_id, member_id)

    def get_members(self, ctx, charter_id: int) -> Tuple[List[int], int]:
        return self.charter_repository.get_members(ctx, charter_id)
