import datetime as dt
from decimal import Decimal

from sqlalchemy import DECIMAL, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from adh6.storage import Base


class MiniRouter(Base):
    __tablename__ = "mini_routers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hardware_mac: Mapped[str] = mapped_column(String(17), nullable=False, unique=True)
    number: Mapped[int | None] = mapped_column(Integer, unique=True)
    model: Mapped[str] = mapped_column(String(20), nullable=False)
    config_state: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now(), onupdate=func.now()
    )


class MiniRouterLoan(Base):
    __tablename__ = "mini_router_loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mini_router_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("mini_routers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    member_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    started_at: Mapped[dt.date] = mapped_column(Date, nullable=False)
    due_date: Mapped[dt.date | None] = mapped_column(Date)
    returned_at: Mapped[dt.date | None] = mapped_column(Date)
    deposit_amount: Mapped[Decimal] = mapped_column(DECIMAL(8, 2), nullable=False)
    payment_method_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("payment_methods.id"))
    deposit_status: Mapped[str] = mapped_column(String(20), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, nullable=False)
