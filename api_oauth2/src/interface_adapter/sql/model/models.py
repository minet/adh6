# coding: utf-8
import time

from authlib.integrations.sqla_oauth2 import OAuth2ClientMixin, OAuth2TokenMixin
from sqlalchemy import Column, ForeignKey, String, Boolean
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True)
    nom = Column(String(255))
    prenom = Column(String(255))
    mail = Column(String(255))
    login = Column(String(255))


class OAuth2Client(Base, OAuth2ClientMixin):
    __tablename__ = 'oauth2_clients'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('members.id', ondelete='CASCADE'))
    user = relationship('Member')
    bypass_consent = Column(Boolean(), nullable=False)


class OAuth2Token(Base, OAuth2TokenMixin):
    __tablename__ = 'oauth2_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('members.id', ondelete='CASCADE'))
    user = relationship('Member')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()