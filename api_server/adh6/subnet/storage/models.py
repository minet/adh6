# coding: utf-8
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
import datetime as dt
from sqlalchemy.orm import Mapped, mapped_column

from adh6.storage import Base


class Vlan(Base):
    __tablename__ = "vlans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero: Mapped[int] = mapped_column(Integer)
    adresses: Mapped[str] = mapped_column(String(255))
    adressesv6: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )
    excluded_addr: Mapped[str] = mapped_column(String(255))
    excluded_addrv6: Mapped[str] = mapped_column(String(255))
