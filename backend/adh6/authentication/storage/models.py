import datetime as dt

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from adh6.storage import Base

from ..enums import AuthenticationMethod, Roles


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(String(128), nullable=False)
    user_login: Mapped[str] = mapped_column(String(255), nullable=False)


class AuthenticationRoleMapping(Base):
    __tablename__ = "role_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    authentication: Mapped[AuthenticationMethod] = mapped_column(
        Enum(AuthenticationMethod), default=AuthenticationMethod.NONE, nullable=False
    )
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Roles] = mapped_column(Enum(Roles), default=Roles.USER, nullable=False)
    expires_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
