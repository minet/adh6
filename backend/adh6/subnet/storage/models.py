import datetime as dt

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from adh6.storage import Base


class Vlan(Base):
    __tablename__ = "vlans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero: Mapped[int | None] = mapped_column(Integer)
    adresses: Mapped[str | None] = mapped_column(String(255))
    adressesv6: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )
    excluded_addr: Mapped[str | None] = mapped_column(String(255))
    excluded_addrv6: Mapped[str | None] = mapped_column(String(255))
