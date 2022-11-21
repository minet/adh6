# coding: utf-8
from sqlalchemy import Column, DECIMAL, String, TEXT, Boolean, DateTime, Integer, Numeric
from sqlalchemy.sql import func, text

from adh6.storage import db
from adh6.storage.sql.trackable import RubyHashTrackable
from adh6.storage.sql.rubydiff import rubydiff


class AccountType(db.Model):
    __tablename__ = 'account_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


class Product(db.Model, RubyHashTrackable):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, unique=True)
    buying_price = Column(DECIMAL(8, 2), nullable=False)
    selling_price = Column(DECIMAL(8, 2), nullable=False)
    name = Column(String(255), nullable=False)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """
        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self.id


class Account(db.Model, RubyHashTrackable):
    __tablename__ = 'accounts'

    id =Column(Integer, primary_key=True, unique=True)
    type= Column(Integer, index=True, nullable=False)
    creation_date = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    name= Column(String(255), nullable=False)
    actif = Column(Boolean(), nullable=False, server_default=text("1"))
    compte_courant = Column(Boolean(), nullable=False, default=False, server_default=text("0"))
    pinned = Column(Boolean(), nullable=False, default=False, server_default=text("0"))
    adherent_id = Column(Integer, index=True, nullable=True)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """
        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self.adherent_id


class Transaction(db.Model, RubyHashTrackable):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    value = Column(DECIMAL(8, 2), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    src = Column(Integer, index=True, nullable=False)
    dst = Column(Integer, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    attachments = Column(TEXT(65535), nullable=False)
    type = Column(Integer, index=True, nullable=False)
    author_id = Column(Integer, index=True, nullable=False)
    pending_validation = Column(Boolean(), nullable=False)
    membership_uuid = Column(String(36), nullable=True)
    is_archive = Column(Boolean, default=False, nullable=True)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self.author_id


class Caisse(db.Model, RubyHashTrackable):
    __tablename__ = 'caisse'

    id = Column(Integer, primary_key=True)
    fond = Column(Numeric(10, 2))
    coffre = Column(Numeric(10, 2))
    date = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())
    linked_transaction = Column(Integer, index=True, nullable=True)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self.id
