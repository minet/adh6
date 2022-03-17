# coding: utf-8
from sqlalchemy import Column, DECIMAL, ForeignKey, String, TEXT, Boolean, Date, DateTime, Integer, Numeric, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import CHAR, Enum

from flask_sqlalchemy import SQLAlchemy

from src.constants import MembershipStatus, MembershipDuration

from src.interface_adapter.sql.model.trackable import RubyHashTrackable
from src.interface_adapter.sql.util.rubydiff import rubydiff

db = SQLAlchemy()

class ApiKey(db.Model):
    __tablename__ = 'api_keys'

    uuid = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)

class Vlan(db.Model):
    __tablename__ = 'vlans'

    id = Column(Integer, primary_key=True)
    numero = Column(Integer)
    adresses = Column(String(255))
    adressesv6 = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    excluded_addr = Column(String(255))
    excluded_addrv6 = Column(String(255))


class Chambre(db.Model, RubyHashTrackable):
    __tablename__ = 'chambres'

    id = Column(Integer, primary_key=True)
    numero = Column(Integer)
    description = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    dernier_adherent = Column(Integer)
    vlan_id = Column(Integer, ForeignKey(Vlan.id))

    vlan = relationship(Vlan, foreign_keys=[vlan_id])

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self

# Suppression of this model from adh6 because it is unused yet do not do the migration yet
"""
class Admin(db.Model):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    roles = Column(String(255))
"""

class Adherent(db.Model, RubyHashTrackable):
    __tablename__ = 'adherents'

    id = Column(Integer, primary_key=True)
    nom = Column(String(255))
    prenom = Column(String(255))
    mail = Column(String(255))
    login = Column(String(255))
    password = Column(String(255))
    chambre_id = Column(Integer, ForeignKey(Chambre.id))

    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    date_de_depart = Column(Date)
    commentaires = Column(String(255))
    mode_association = Column(
        DateTime,
        server_default=text("'2011-04-30 17:50:17'")
    )
    access_token = Column(String(255))
    subnet = Column(String(255))
    ip = Column(String(255))
    ldap_login = Column(String(255))
    is_naina = Column(Boolean, default=False, nullable=False)

    # admin_id = Column(Integer, ForeignKey(Admin.id), nullable=True)

    datesignedminet = Column(DateTime, nullable=True)
    datesignedhosting = Column(DateTime, nullable=True)
    mailinglist = Column(Boolean, nullable=False, default=True)

    # admin = relationship('Admin', foreign_keys=[admin_id])
    chambre = relationship('Chambre', foreign_keys=[chambre_id])
    memberships = relationship(
        'Membership', 
        back_populates="adherent",
        cascade="all, delete",
        passive_deletes=True
    )

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


class Inscription(db.Model):
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


class Modification(db.Model):
    __tablename__ = 'modifications'

    id = Column(Integer, primary_key=True)
    adherent_id = Column(Integer, index=True)
    action = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    utilisateur_id = Column(Integer, index=True)


class Device(db.Model, RubyHashTrackable):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    mac = Column(String(255))
    ip = Column(String(255))
    adherent_id = Column(Integer, ForeignKey(Adherent.id), nullable=False)
    adherent = relationship(Adherent, foreign_keys=[adherent_id])
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    last_seen = Column(DateTime)
    ipv6 = Column(String(255))
    type = Column(Integer)
    mab = Column(Boolean, nullable=False, default=False, server_default='0')

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


class Routeur(db.Model, RubyHashTrackable):
    __tablename__ = 'routeurs'

    id = Column(Integer, primary_key=True)
    mac = Column(String(255))
    ip = Column(String(255))
    adherent_id = Column(Integer, ForeignKey(Adherent.id), nullable=False)
    adherent = relationship(Adherent, foreign_keys=[adherent_id])
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

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


class Switch(db.Model):
    __tablename__ = 'switches'

    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    ip = Column(String(15))
    communaute = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Port(db.Model):
    __tablename__ = 'ports'

    id = Column(Integer, primary_key=True)
    rcom = Column(Integer)
    numero = Column(String(255))
    oid = Column(String(255))
    switch_id = Column(Integer, ForeignKey(Switch.id), nullable=False)
    chambre_id = Column(Integer, ForeignKey(Chambre.id), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    switch = relationship(Switch, foreign_keys=[switch_id])
    chambre = relationship(Chambre, foreign_keys=[chambre_id])


class Adhesion(db.Model):
    __tablename__ = 'adhesions'

    id = Column(Integer, primary_key=True)
    adherent_id = Column(Integer, ForeignKey(Adherent.id), nullable=False)
    adherent = relationship(Adherent)
    depart = Column(DateTime, nullable=False)
    fin = Column(DateTime, nullable=False)


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
        return self


class Account(db.Model, RubyHashTrackable):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, unique=True)
    type = Column(ForeignKey('account_types.id'), nullable=False, index=True)
    creation_date = Column(DateTime, nullable=False)
    name = Column(String(255), nullable=False)
    actif = Column(Boolean(), nullable=False)
    compte_courant = Column(Boolean(), nullable=False, default=False)
    pinned = Column(Boolean(), nullable=False, default=False)
    adherent_id = Column(Integer, ForeignKey('adherents.id'), nullable=True)

    adherent = relationship('Adherent', foreign_keys=[adherent_id])
    account_type = relationship('AccountType', foreign_keys=[type])

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """
        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self


class Transaction(db.Model, RubyHashTrackable):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    value = Column(DECIMAL(8, 2), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    src = Column(ForeignKey('accounts.id'), nullable=False, index=True)
    dst = Column(ForeignKey('accounts.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    attachments = Column(TEXT(65535), nullable=False)
    type = Column(ForeignKey('payment_methods.id'), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey('adherents.id'), nullable=False, index=True)
    pending_validation = Column(Boolean(), nullable=False)
    membership_uuid = Column(String(36), nullable=True)
    is_archive = Column(Boolean, default=False, nullable=True)

    author = relationship('Adherent', foreign_keys=[author_id])
    dst_account = relationship('Account', foreign_keys=[dst])
    src_account = relationship('Account', foreign_keys=[src])
    payment_method = relationship('PaymentMethod', foreign_keys=[type])

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self


class Caisse(db.Model, RubyHashTrackable):
    __tablename__ = 'caisse'

    id = Column(Integer, primary_key=True)
    fond = Column(Numeric(10, 2))
    coffre = Column(Numeric(10, 2))
    date = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    linked_transaction = Column(Integer, ForeignKey('transactions.id'), nullable=True, index=True)
    transaction = relationship('Transaction', foreign_keys=[linked_transaction])

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """

        modif = rubydiff(snap_before, snap_after)
        modif = '--- !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n' + modif
        return modif

    def get_related_member(self):
        return self


class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs'

    id = Column(Integer, primary_key=True)
    nom = Column(String(255))
    access = Column(Integer)
    email = Column(String(255))
    login = Column(String(255))
    password_hash = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    access_token = Column(String(255))


class MailTemplates(db.Model):
    __tablename__ = 'mail_templates'

    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    sujet = Column(String(255))
    template = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Membership(db.Model):
    __tablename__ = "membership"

    uuid = Column(String(36), primary_key=True)
    account_id = Column(Integer, ForeignKey(Account.id), nullable=True)
    create_at = Column(DateTime)
    duration = Column(Enum(MembershipDuration), default=MembershipDuration.NONE, nullable=False)
    has_room = Column(Boolean, default=True, nullable=False)
    first_time = Column(Boolean, default=False, nullable=False)
    adherent_id = Column(Integer, ForeignKey(Adherent.id), nullable=False)
    payment_method_id = Column(Integer, ForeignKey(PaymentMethod.id), nullable=True)
    products = Column(String(255), nullable=True)
    status = Column(Enum(MembershipStatus), default=MembershipStatus.INITIAL, nullable=False)
    update_at = Column(DateTime)

    adherent = relationship('Adherent', foreign_keys=[adherent_id], back_populates="memberships")
    account = relationship('Account', foreign_keys=[account_id])
    payment_method = relationship('PaymentMethod', foreign_keys=[payment_method_id])
