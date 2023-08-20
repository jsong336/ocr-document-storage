from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


class PostgresConnectionConfig(BaseModel):
    drivername: str
    username: str
    password: str
    host: str
    port: str


class Settings(BaseSettings):
    postgres_connection: PostgresConnectionConfig
    model_config = SettingsConfigDict(env_prefix="CHAK_", case_sensitive=False)


settings = Settings()
