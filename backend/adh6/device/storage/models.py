import datetime as dt

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from adh6.storage import Base
from adh6.storage.sql.rubydiff import rubydiff
from adh6.storage.sql.trackable import RubyHashTrackable


class Device(Base, RubyHashTrackable):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mac: Mapped[str | None] = mapped_column(String(255))
    ip: Mapped[str | None] = mapped_column(String(255))
    adherent_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )
    last_seen: Mapped[dt.datetime | None] = mapped_column(DateTime)
    ipv6: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[int | None] = mapped_column(Integer)
    mab: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    name: Mapped[str | None] = mapped_column(String(255))
    wifi_password: Mapped[str | None] = mapped_column(String(63))

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """
        modif = rubydiff(snap_before, snap_after)
        if snap_after is None:
            proper_mac = snap_before.get("mac", "").upper().replace(":", "-")
            return f"---\ndevice: Suppression du périphérique {proper_mac}\n"

        modif = "device: !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n" + modif
        return modif

    def get_related_member(self):
        return self.adherent_id
