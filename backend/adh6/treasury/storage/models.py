import datetime as dt

from sqlalchemy import DECIMAL, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from adh6.storage import Base
from adh6.storage.sql.rubydiff import rubydiff
from adh6.storage.sql.trackable import RubyHashTrackable


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class Product(Base, RubyHashTrackable):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    buying_price: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False)
    selling_price: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        modif = rubydiff(snap_before, snap_after)
        modif = "--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n" + modif
        return modif

    def get_related_member(self):
        return self.id


class Transaction(Base, RubyHashTrackable):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False)
    timestamp: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    membership_uuid: Mapped[str | None] = mapped_column(String(36), nullable=True)
    api_key_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        modif = rubydiff(snap_before, snap_after)
        modif = "--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n" + modif
        return modif

    def get_related_member(self):
        return self.author_id
