from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _recipients(raw: str) -> list[str]:
    """Split a comma-separated list, dropping empty entries.

    Without the filter, an empty variable would yield [""], a non-empty list, and the empty
    address would travel all the way to SMTP.
    """
    return [address.strip() for address in raw.split(",") if address.strip()]


class Settings(BaseSettings):
    debug: bool = False
    testing: bool = False
    secret_key: str | None = None

    # Database settings
    database_username: str | None = None
    database_password: str | None = None
    database_host: str | None = None
    database_db_name: str = "adh6"

    sqlalchemy_echo: bool = False
    sqlalchemy_pool_size: int = 5
    sqlalchemy_max_overflow: int = 10
    sqlalchemy_pool_recycle: int = 3600 * 4

    @computed_field
    @property
    def database_url(self) -> str:
        if self.testing:
            # File-backed sqlite keeps a shared database across test sessions.
            return "sqlite+aiosqlite:///./.adh6-test.db"

        if not self.database_host:
            # Default fallback if needed, or let it fail/be empty if that's preferred
            return "mysql+aiomysql://user:pass@localhost/adh6"

        return f"mysql+aiomysql://{self.database_username}:{self.database_password}@{self.database_host}/{self.database_db_name}"

    # SMTP
    smtp_server: str | None = None
    smtp_port: int = 25
    mail_from: str = "no-reply@minet.net"
    # Emergency switch: when false, mails are logged instead of sent. In dev and preprod the real
    # safety net is mailpit, which intercepts everything and shows the rendered mail.
    mail_enabled: bool = True
    # Language used when the member has no stored preference. A mail is sent in ONE language.
    mail_default_language: str = "fr"
    # Comma-separated lists. Empty means nobody, which disables the corresponding admin mail.
    mail_treasury_recipients: str = ""
    mail_minirouter_recipients: str = ""
    # minet_dark.png is the black-text variant, for a light background -- which is what the
    # mail card uses. minet_light.png is the white-text one, for dark backgrounds.
    # Public host, used to build the ADH6 links inside admin mails. The reverse proxy already
    # receives it as ADH6_URL; the backend needs it too now that it sends mails.
    adh6_url: str = "adh6.minet.net"
    # Empty means no logo, rather than a broken image.
    mail_logo_url: str = "https://minet.net/minet_dark.png"

    @computed_field
    @property
    def treasury_recipients(self) -> list[str]:
        return _recipients(self.mail_treasury_recipients)

    @computed_field
    @property
    def minirouter_recipients(self) -> list[str]:
        return _recipients(self.mail_minirouter_recipients)

    # ELK
    elk_enabled: bool = False
    elk_hosts: str = "http://localhost:9200"
    elk_user: str | None = None
    elk_secret: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")


settings = Settings()
