# coding: utf-8
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.sql import func

from adh6.storage.sql.trackable import RubyHashTrackable
from adh6.storage.sql.rubydiff import rubydiff

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
session = db.session


# Suppression of this model from adh6 because it is unused yet do not do the migration yet
class Admin(db.Model):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    roles = Column(String(255))


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
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())


class Modification(db.Model):
    __tablename__ = 'modifications'

    id = Column(Integer, primary_key=True)
    adherent_id = Column(Integer, index=True)
    action = Column(Text)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())
    utilisateur_id = Column(Integer, index=True)


class Routeur(db.Model, RubyHashTrackable):
    __tablename__ = 'routeurs'

    id = Column(Integer, primary_key=True)
    mac = Column(String(255))
    ip = Column(String(255))
    adherent_id = Column(Integer, index=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())

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
        return self.adherent_id


class Adhesion(db.Model):
    __tablename__ = 'adhesions'

    id = Column(Integer, primary_key=True)
    adherent_id = Column(Integer, index=True, nullable=False)
    depart = Column(DateTime, nullable=False)
    fin = Column(DateTime, nullable=False)


class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs'

    id = Column(Integer, primary_key=True)
    nom = Column(String(255))
    access = Column(Integer)
    email = Column(String(255))
    login = Column(String(255))
    password_hash = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())
    access_token = Column(String(255))


class MailTemplates(db.Model):
    __tablename__ = 'mail_templates'

    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    sujet = Column(String(255))
    template = Column(Text)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_onupdate=func.now())


