# coding: utf-8
import time

from authlib.integrations.sqla_oauth2 import OAuth2ClientMixin, OAuth2AuthorizationCodeMixin, OAuth2TokenMixin
from sqlalchemy import Column, DECIMAL, ForeignKey, String, TIMESTAMP, TEXT, Boolean
from sqlalchemy import Date, DateTime, Integer, \
    Numeric, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.interface_adapter.sql.model.trackable import RubyHashTrackable
from src.interface_adapter.sql.util.rubydiff import rubydiff

Base = declarative_base()


class Vlan(Base):
    __tablename__ = 'vlans'

    id = Column(Integer, primary_key=True)
    numero = Column(Integer)
    adresses = Column(String(255))
    adressesv6 = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Chambre(Base):
    __tablename__ = 'chambres'

    id = Column(Integer, primary_key=True)
    numero = Column(Integer)
    description = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    dernier_adherent = Column(Integer)
    vlan_id = Column(Integer, ForeignKey(Vlan.id))
    vlan = relationship(Vlan)


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    roles = Column(String(255))


class Adherent(Base, RubyHashTrackable):
    __tablename__ = 'adherents'

    id = Column(Integer, primary_key=True)
    nom = Column(String(255))
    prenom = Column(String(255))
    mail = Column(String(255))
    login = Column(String(255))
    password = Column(String(255))
    chambre_id = Column(Integer, ForeignKey(Chambre.id))
    chambre = relationship(Chambre)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    date_de_depart = Column(Date)
    commentaires = Column(String(255))
    mode_association = Column(
        DateTime,
        server_default=text("'2011-04-30 17:50:17'")
    )
    access_token = Column(String(255))

    admin_id = Column(Integer, ForeignKey(Admin.id), nullable=True)

    admin = relationship('Admin', foreign_keys=[admin_id])

    def take_snapshot(self) -> dict:
        snap = super().take_snapshot()
        if 'password' in snap:
            del snap['password']  # Let's not track the password changes, this is none of our business. :)
        return snap

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self


class Caisse(Base, RubyHashTrackable):
    __tablename__ = 'caisse'

    id = Column(Integer, primary_key=True)
    fond = Column(Numeric(10, 2))
    coffre = Column(Numeric(10, 2))
    date = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    transaction = Column(ForeignKey('transactions.id'), nullable=True, index=True)

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self


class Inscription(Base):
    __tablename__ = 'inscriptions'

    id = Column(Integer, primary_key=True)
    nom = Column(String(255))
    prenom = Column(String(255))
    email = Column(String(255))
    login = Column(String(255))
    password = Column(String(255))
    chambre_id = Column(Integer, index=True)
    duree_cotisation = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Modification(Base):
    __tablename__ = 'modifications'

    id = Column(Integer, primary_key=True)
    adherent_id = Column(Integer, index=True)
    action = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    utilisateur_id = Column(Integer, index=True)


class Device(Base, RubyHashTrackable):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    mac = Column(String(255))
    ip = Column(String(255))
    adherent_id = Column(Integer, ForeignKey(Adherent.id), nullable=False)
    adherent = relationship(Adherent)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    last_seen = Column(DateTime)
    ipv6 = Column(String(255))
    type = Column(String(255))

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """
        modif = rubydiff(snap_before, snap_after)
        if snap_after is None:
            proper_mac = snap_before.get('mac').upper().replace(":", "-")
            return (
                "---\n"
                "device: Suppression du périphérique {}\n".format(proper_mac)
            )

        modif = 'device: !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self.adherent


class Switch(Base):
    __tablename__ = 'switches'

    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    ip = Column(String(255))
    communaute = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Port(Base):
    __tablename__ = 'ports'

    id = Column(Integer, primary_key=True)
    rcom = Column(Integer)
    numero = Column(String(255))
    oid = Column(String(255))
    switch_id = Column(Integer, ForeignKey(Switch.id), nullable=False)
    switch = relationship(Switch)
    chambre_id = Column(Integer, ForeignKey(Chambre.id), nullable=False)
    chambre = relationship(Chambre)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Adhesion(Base):
    __tablename__ = 'adhesions'

    id = Column(Integer, primary_key=True)
    adherent_id = Column(Integer, ForeignKey(Adherent.id), nullable=False)
    adherent = relationship(Adherent)
    depart = Column(DateTime, nullable=False)
    fin = Column(DateTime, nullable=False)


class AccountType(Base):
    __tablename__ = 'account_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


class PaymentMethod(Base):
    __tablename__ = 'payment_methods'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


class Product(Base, RubyHashTrackable):
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
        return self


class Account(Base, RubyHashTrackable):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, unique=True)
    type = Column(ForeignKey('account_types.id'), nullable=False, index=True)
    creation_date = Column(DateTime, nullable=False)
    name = Column(String(255), nullable=False)
    actif = Column(Boolean(), nullable=False)
    adherent_id = Column(Integer, ForeignKey('adherents.id'), nullable=True)

    adherent = relationship('Adherent', foreign_keys=[adherent_id])
    account_type = relationship('AccountType')

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """
        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self


class Transaction(Base, RubyHashTrackable):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    value = Column(DECIMAL(8, 2), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    src = Column(ForeignKey('accounts.id'), nullable=False, index=True)
    dst = Column(ForeignKey('accounts.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    attachments = Column(TEXT(65535), nullable=False)
    type = Column(ForeignKey('payment_methods.id'), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey('adherents.id'), nullable=False)

    author = relationship('Adherent', foreign_keys=[author_id])
    dst_account = relationship('Account', foreign_keys=[dst])
    src_account = relationship('Account', foreign_keys=[src])
    payment_method = relationship('PaymentMethod')

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self


class OAuth2Client(Base, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('adherents.id', ondelete='CASCADE'))
    user = relationship('Adherent')
    bypass_consent = Column(Boolean(), nullable=False)


class OAuth2AuthorizationCode(Base, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('adherents.id', ondelete='CASCADE'))
    user = relationship('Adherent')


class OAuth2Token(Base, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('adherents.id', ondelete='CASCADE'))
    user = relationship('Adherent')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()