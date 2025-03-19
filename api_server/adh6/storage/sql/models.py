import datetime as dt

from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from adh6.storage.sql.rubydiff import rubydiff
from adh6.storage.sql.trackable import RubyHashTrackable


class Base(DeclarativeBase):
    pass


db = SQLAlchemy()


# Suppression of this model from adh6 because it is unused yet do not do the migration yet
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    roles = Column(String(255))


class Inscription(Base):
    __tablename__ = "inscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[int] = mapped_column(String(255))
    prenom: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    login: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
    chambre_id: Mapped[int] = mapped_column(Integer, index=True)
    duree_cotisation: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )


class Modification(Base):
    __tablename__ = "modifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adherent_id: Mapped[int] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )
    utilisateur_id: Mapped[int] = mapped_column(Integer, index=True)


class Routeur(Base, RubyHashTrackable):
    __tablename__ = "routeurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mac: Mapped[str] = mapped_column(String(255))
    ip: Mapped[str] = mapped_column(String(255))
    adherent_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )

    def serialize_snapshot_diff(self, snap_before: dict, snap_after: dict) -> str:
        """
        Override this method to add the prefix.
        """
        modif = rubydiff(snap_before, snap_after)
        if snap_after is None:
            proper_mac = snap_before.get("mac").upper().replace(":", "-")
            return f"---\ndevice: Suppression du périphérique {proper_mac}\n"

        modif = "device: !ruby/hash:ActiveSupport::HashWithIndifferentAccess\n" + modif
        return modif

    def get_related_member(self):
        return self.adherent_id


class Adhesion(Base):
    __tablename__ = "adhesions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adherent_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    depart: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)
    fin: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str] = mapped_column(String(255))
    access: Mapped[str] = mapped_column(Integer)
    email: Mapped[str] = mapped_column(String(255))
    login: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )
    access_token: Mapped[str] = mapped_column(String(255))


class MailTemplates(Base):
    __tablename__ = "mail_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(255))
    sujet: Mapped[str] = mapped_column(String(255))
    template: Mapped[str] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )
