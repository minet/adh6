# coding: utf-8
from enum import unique
from sqlalchemy import Column, String, Boolean, Date, DateTime, Integer, Text
from sqlalchemy.sql import func, text
from sqlalchemy.sql.sqltypes import Enum

from adh6.constants import MembershipStatus, MembershipDuration

from adh6.storage import db
from adh6.storage.sql.trackable import RubyHashTrackable
from adh6.storage.sql.rubydiff import rubydiff


class Adherent(db.Model, RubyHashTrackable):
    __tablename__ = 'adherents'

    id = Column(Integer, primary_key=True)
    nom = Column(String(255))
    prenom = Column(String(255))
    mail = Column(String(255))
    login = Column(String(255))
    password = Column(String(255))
    chambre_id = Column(Integer, index=True)

    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())
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
    datesignedminet = Column(DateTime, nullable=True)
    datesignedhosting = Column(DateTime, nullable=True)
    mail_membership = Column(Integer, nullable=False, default=0, server_default='1')
    mailinglist = Column(Boolean, nullable=True, default=True)

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
        return self.id


class Membership(db.Model):
    __tablename__ = "membership"

    uuid = Column(String(36), primary_key=True)
    account_id = Column(Integer, index=True, nullable=True)
    duration = Column(Enum(MembershipDuration), default=MembershipDuration.NONE, nullable=False)
    has_room = Column(Boolean, default=True, nullable=False)
    first_time = Column(Boolean, default=False, nullable=False)
    adherent_id = Column(Integer, index=True, nullable=False)
    payment_method_id = Column(Integer, index=True, nullable=True)
    products = Column(String(255), nullable=True)
    status = Column(Enum(MembershipStatus), default=MembershipStatus.INITIAL, nullable=False)
    create_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    update_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())

class NotificationTemplate(db.Model):
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, unique=True)
    template = Column(Text, nullable=True)