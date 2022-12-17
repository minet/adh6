import typing as t
from adh6.entity import Member
from adh6.decorator import log_call

from .interfaces import MailinglistRepository


class MailinglistManager:
    def __init__(self, mailinglist_repository: MailinglistRepository) -> None:
        self.mailinglist_repository = mailinglist_repository
    
    @log_call
    def get_member_mailinglist(self, member: Member) -> int:
        return self.mailinglist_repository.get_from_member(member.id)
        
    @log_call 
    def update_member_mailinglist(self, member: Member, value: int) -> None:
        self.mailinglist_repository.update_from_member(member.id, value)
    
    @log_call
    def get_members(self, value: int) -> t.List[int]:
        return self.mailinglist_repository.list_members(value)
