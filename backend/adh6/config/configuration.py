from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # ELK
    elk_enabled: bool = False
    elk_hosts: str = "http://localhost:9200"
    elk_user: str | None = None
    elk_secret: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")


settings = Settings()
