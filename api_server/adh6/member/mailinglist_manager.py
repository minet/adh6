import typing as t
from adh6.exceptions import MemberNotFoundError

from .interfaces import MailinglistRepository, MemberRepository


class MailinglistManager:
    def __init__(self, member_repository: MemberRepository, mailinglist_repository: MailinglistRepository) -> None:
        self.member_repository = member_repository
        self.mailinglist_repository = mailinglist_repository
    
    def get_member_mailinglist(self, member_id: int) -> int:
        m = self.member_repository.get_by_id(member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        return self.mailinglist_repository.get_from_member(member_id)
         
    def update_member_mailinglist(self, member_id: int, value: int) -> None:
        m = self.member_repository.get_by_id(member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        self.mailinglist_repository.update_from_member(member_id, value)
    
    def get_members(self, value: int) -> t.List[int]:
        return self.mailinglist_repository.list_members(value)
