from sqlalchemy import Column, String, Enum, Integer

from adh6.authentication.enums import AuthenticationMethod, Roles
from adh6.storage import db


class ApiKey(db.Model):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True)
    value = Column(String(128), nullable=False)
    user_login = Column(String(255), nullable=False)


class AuthenticationRoleMapping(db.Model):
    __tablename__ = "role_mappings"
    id = Column(Integer, primary_key=True)
    authentication = Column(Enum(AuthenticationMethod), default=AuthenticationMethod.NONE, nullable=False)
    identifier = Column(String(255), nullable=False)
    role = Column(Enum(Roles), default=Roles.USER, nullable=False)
