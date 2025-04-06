import datetime as dt
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text
from sqlalchemy.sql.sqltypes import Enum

from adh6.constants import MembershipDuration, MembershipStatus
from adh6.storage import Base
from adh6.storage.sql.rubydiff import rubydiff
from adh6.storage.sql.trackable import RubyHashTrackable
def abc(test: int):
    print(test)

class Adherent(Base, RubyHashTrackable):
    __tablename__ = "adherents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str | None] = mapped_column(String(255))
    prenom: Mapped[str | None] = mapped_column(String(255))
    mail: Mapped[str | None] = mapped_column(String(255))
    login: Mapped[str | None] = mapped_column(String(255))
    password: Mapped[str | None] = mapped_column(String(255))
    chambre_id: Mapped[int | None] = mapped_column(Integer, index=True)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )
    date_de_depart: Mapped[dt.date | None] = mapped_column(Date)
    commentaires: Mapped[str | None] = mapped_column(String(255))
    mode_association: Mapped[dt.datetime | None] = mapped_column(DateTime, server_default=text("'2011-04-30 17:50:17'"))
    access_token: Mapped[str | None | None] = mapped_column(String(255))
    subnet: Mapped[str | None] = mapped_column(String(255))
    ip: Mapped[str | None] = mapped_column(String(255))
    ldap_login: Mapped[str | None | None] = mapped_column(String(255))
    is_naina: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    datesignedminet: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    datesignedhosting: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    mail_membership: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="1")
    mailinglist: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=True)

    def take_snapshot(self) -> dict:
        snap = super().take_snapshot()
        if "password" in snap:
            del snap["password"]  # Let's not track the password changes, this is none of our business. :)
        return snap

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = "--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n" + modif
        return modif

    def get_related_member(self):
        return self.id


class Membership(Base):
    __tablename__ = "membership"

    uuid: Mapped[str] = mapped_column(String(36), primary_key=True)
    account_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    duration: Mapped[Any] = mapped_column(
        Enum(MembershipDuration), default=MembershipDuration.NONE, nullable=False
    )  # TODO: typing
    has_room: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    first_time: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    adherent_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    payment_method_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    products: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[Any] = mapped_column(
        Enum(MembershipStatus), default=MembershipStatus.INITIAL, nullable=False
    )  # TODO: typing
    create_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    update_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    template: Mapped[str | None] = mapped_column(Text, nullable=True)  # why Text ? Vs String ?
