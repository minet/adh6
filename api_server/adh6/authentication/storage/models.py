from sqlalchemy import Column, String, Integer, Enum

from adh6.authentication import AuthenticationMethod, Roles
from adh6.storage import db


class ApiKey(db.Model):
    uuid = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)


class AuthenticationRoleMapping(db.Model):
    id = Column(Integer, primary_key=True)
    authentication = Column(Enum(AuthenticationMethod), default=AuthenticationMethod.NONE, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(Roles), default=Roles.USER, nullable=False)
