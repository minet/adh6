import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from adh6.storage import Base
from adh6.subnet.storage.models import Vlan


class Chambre(Base):
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
    vlan_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("vlans.id"), index=True)

    vlan: Mapped["Vlan"] = relationship("Vlan", lazy="selectin")


class RoomMemberLink(Base):
    __tablename__ = "rooms_members_association"
    room_id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    member_id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
