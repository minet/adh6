import datetime as dt

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from adh6.storage import Base
from adh6.storage.sql.rubydiff import rubydiff
from adh6.storage.sql.trackable import RubyHashTrackable


class Chambre(Base, RubyHashTrackable):
    __tablename__ = "chambres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )
    dernier_adherent: Mapped[int | None] = mapped_column(Integer)
    vlan_id: Mapped[int | None] = mapped_column(Integer, index=True)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = "--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n" + modif
        return modif

    def get_related_member(self):
        return self.id


class RoomMemberLink(Base):
    __tablename__ = "rooms_members_association"
    room_id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    member_id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
