# coding: utf-8
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func

from adh6.storage import db
from adh6.storage.sql.trackable import RubyHashTrackable
from adh6.storage.sql.rubydiff import rubydiff


class Chambre(db.Model, RubyHashTrackable):
    __tablename__ = 'chambres'

    id = Column(Integer, primary_key=True)
    numero = Column(Integer)
    description = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())
    dernier_adherent = Column(Integer)
    vlan_id = Column(Integer, index=True)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self.id


class RoomMemberLink(db.Model):
    __tablename__ = 'rooms_members_association'
    room_id = Column(Integer, nullable=False, primary_key=True)
    member_id = Column(Integer, nullable=False, primary_key=True)
