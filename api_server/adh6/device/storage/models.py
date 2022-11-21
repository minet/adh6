# coding: utf-8
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.sql import func

from adh6.storage import db
from adh6.storage.sql.trackable import RubyHashTrackable
from adh6.storage.sql.rubydiff import rubydiff


class Device(db.Model, RubyHashTrackable):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    mac = Column(String(255))
    ip = Column(String(255))
    adherent_id = Column(Integer, index=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())
    last_seen = Column(DateTime)
    ipv6 = Column(String(255))
    type = Column(Integer)
    mab = Column(Boolean, nullable=False, default=False, server_default='0')

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """
        modif = rubydiff(snap_before, snap_after)
        if snap_after is None:
            proper_mac = snap_before.get('mac', '').upper().replace(":", "-")
            return (
                "---\n"
                "device: Suppression du périphérique {}\n".format(proper_mac)
            )

        modif = 'device: !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self.adherent_id
