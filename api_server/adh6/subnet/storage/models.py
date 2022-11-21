# coding: utf-8
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func

from adh6.storage import db

class Vlan(db.Model):
    __tablename__ = 'vlans'

    id = Column(Integer, primary_key=True)
    numero = Column(Integer)
    adresses = Column(String(255))
    adressesv6 = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())
    excluded_addr = Column(String(255))
    excluded_addrv6 = Column(String(255))
