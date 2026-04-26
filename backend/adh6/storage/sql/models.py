import datetime as dt

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


# Suppression of this model from adh6 because it is unused yet do not do the migration yet
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    roles = Column(String(255))


class Inscription(Base):
    __tablename__ = "inscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[int | None] = mapped_column(String(255))
    prenom: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    login: Mapped[str | None] = mapped_column(String(255))
    password: Mapped[str | None] = mapped_column(String(255))
    chambre_id: Mapped[int | None] = mapped_column(Integer, index=True)
    duree_cotisation: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )


class Routeur(Base):
    __tablename__ = "routeurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mac: Mapped[str | None] = mapped_column(String(255))
    ip: Mapped[str | None] = mapped_column(String(255))
    adherent_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )


class Adhesion(Base):
    __tablename__ = "adhesions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adherent_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    depart: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)
    fin: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str | None] = mapped_column(String(255))
    access: Mapped[str | None] = mapped_column(Integer)
    email: Mapped[str | None] = mapped_column(String(255))
    login: Mapped[str | None] = mapped_column(String(255))
    password_hash: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )
    access_token: Mapped[str | None] = mapped_column(String(255))


class MailTemplates(Base):
    __tablename__ = "mail_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str | None] = mapped_column(String(255))
    sujet: Mapped[str | None] = mapped_column(String(255))
    template: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_onupdate=func.now()
    )
