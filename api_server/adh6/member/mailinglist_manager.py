from typing import List
from adh6.exceptions import MemberNotFoundError
from adh6.member.interfaces.mailinglist_repository import MailinglistRepository
from adh6.member.interfaces.member_repository import MemberRepository


class MailinglistManager:
    def __init__(self, member_repository: MemberRepository, mailinglist_repository: MailinglistRepository) -> None:
        self.member_repository = member_repository
        self.mailinglist_repository = mailinglist_repository
    
    def get_member_mailinglist(self, ctx, member_id: int) -> int:
        m = self.member_repository.get_by_id(ctx, member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        return self.mailinglist_repository.get_from_member(ctx, member_id)
         
    def update_member_mailinglist(self, ctx, member_id: int, value: int) -> None:
        m = self.member_repository.get_by_id(ctx, member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        self.mailinglist_repository.update_from_member(ctx, member_id, value)
    
    def get_members(self, ctx, value: int) -> List[int]:
        return self.mailinglist_repository.list_members(ctx, value)
