from typing import Any
from sqlalchemy import String, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from adh6.authentication import AuthenticationMethod, Roles
from adh6.storage import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(String(128), nullable=False)
    user_login: Mapped[str] = mapped_column(String(255), nullable=False)


class AuthenticationRoleMapping(Base):
    __tablename__ = "role_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    authentication: Mapped[Any] = mapped_column(
        Enum(AuthenticationMethod), default=AuthenticationMethod.NONE, nullable=False
    )  # TODO: typing
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Any] = mapped_column(Enum(Roles), default=Roles.USER, nullable=False)  # TODO: typing
