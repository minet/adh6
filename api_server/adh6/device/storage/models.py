# coding: utf-8
from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from adh6.storage import Base
from adh6.storage.sql.trackable import RubyHashTrackable
from adh6.storage.sql.rubydiff import rubydiff
import datetime as dt

class Device(Base, RubyHashTrackable):
    __tablename__ = 'devices'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mac: Mapped[str] = mapped_column(String(255))
    ip: Mapped[str] = mapped_column(String(255))
    adherent_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())
    last_seen: Mapped[dt.datetime] = mapped_column(DateTime)
    ipv6: Mapped[str] = mapped_column(String(255))
    type: Mapped[int] = mapped_column(Integer)
    mab: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default='0')

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
