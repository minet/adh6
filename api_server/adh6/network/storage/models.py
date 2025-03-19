# coding: utf-8
from sqlalchemy.orm import Mapped, mapped_column
import datetime as dt

from adh6.storage import Base
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func


class Switch(Base):
    __tablename__ = 'switches'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(255))
    ip: Mapped[str] = mapped_column(String(15))
    communaute: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())


class Port(Base):
    __tablename__ = 'ports'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rcom: Mapped[int] = mapped_column(Integer)
    numero: Mapped[str] = mapped_column(String(255), nullable=False)
    oid: Mapped[str] = mapped_column(String(255), nullable=False)
    switch_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    chambre_id: Mapped[int] = mapped_column(Integer, index=True, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())
