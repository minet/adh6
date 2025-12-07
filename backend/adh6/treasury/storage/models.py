import datetime as dt

from sqlalchemy import DECIMAL, TEXT, Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func, text

from adh6.storage import Base
from adh6.storage.sql.rubydiff import rubydiff
from adh6.storage.sql.trackable import RubyHashTrackable


class AccountType(Base):
    __tablename__ = "account_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class Product(Base, RubyHashTrackable):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    buying_price: Mapped[float] = mapped_column(
        DECIMAL(8, 2), nullable=False
    )  # TODO: I think Numeric is better than DECIMAL, mais il faudrait se renseigner
    selling_price: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """
        modif = rubydiff(snap_before, snap_after)
        modif = "--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n" + modif
        return modif

    def get_related_member(self):
        return self.id


class Account(Base, RubyHashTrackable):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    type: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    creation_date: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default=text("1"))
    compte_courant: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False, server_default=text("0"))
    pinned: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False, server_default=text("0"))
    adherent_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """
        modif = rubydiff(snap_before, snap_after)
        modif = "--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n" + modif
        return modif

    def get_related_member(self):
        return self.adherent_id


class Transaction(Base, RubyHashTrackable):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False)
    timestamp: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    src: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    dst: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    attachments: Mapped[str] = mapped_column(
        TEXT(65535), nullable=False
    )  # TODO: regarder String vs TEXT et choisir le plus adapté
    type: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    pending_validation: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    is_archive: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)
    membership_uuid: Mapped[str | None] = mapped_column(String(36), nullable=True)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = "--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n" + modif
        return modif

    def get_related_member(self):
        return self.author_id


class Caisse(Base, RubyHashTrackable):
    __tablename__ = "caisse"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fond: Mapped[float | None] = mapped_column(Numeric(10, 2))
    coffre: Mapped[float | None] = mapped_column(Numeric(10, 2))
    date: Mapped[dt.datetime | None] = mapped_column(DateTime)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )
    linked_transaction: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = "--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n" + modif
        return modif

    def get_related_member(self):
        return self.id
