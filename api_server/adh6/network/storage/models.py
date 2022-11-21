# coding: utf-8
from adh6.storage import db
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func


class Switch(db.Model):
    __tablename__ = 'switches'

    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    ip = Column(String(15))
    communaute = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())


class Port(db.Model):
    __tablename__ = 'ports'

    id = Column(Integer, primary_key=True)
    rcom = Column(Integer)
    numero = Column(String(255), nullable=False)
    oid = Column(String(255), nullable=False)
    switch_id = Column(Integer, index=True, nullable=False)
    chambre_id = Column(Integer, index=True, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())

