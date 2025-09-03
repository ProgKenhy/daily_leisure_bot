from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class MyBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore'
    )

class PostgresSettings(MyBaseSettings):
    HOST: str = Field(alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    USER: str = Field(alias="POSTGRES_USER")
    PASS: SecretStr = Field(alias="POSTGRES_PASS")
    NAME: str = Field(alias="POSTGRES_NAME")

    @property
    def ASYNC_URL(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASS.get_secret_value()}@{self.HOST}:{self.port}/{self.NAME}"

    @property
    def SYNC_URL(self) -> str:
        return f"postgresql+psycopg2://{self.USER}:{self.PASS.get_secret_value()}@{self.HOST}:{self.port}/{self.NAME}"

class BotSettings(MyBaseSettings):
    TOKEN: str = Field(alias="BOT_TOKEN")

class Settings(MyBaseSettings):
    database: PostgresSettings = PostgresSettings()
    bot: BotSettings = BotSettings()

    DEBUG: bool = Field(alias="DEBUG", default=False)
    ENVIRONMENT: str = Field(alias="ENVIRONMENT", default="development")

settings = Settings()