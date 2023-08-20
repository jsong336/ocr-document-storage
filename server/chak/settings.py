from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


class MongoDbConfig(BaseModel):
    connection_uri: str
    database: str


class Settings(BaseSettings):
    mongodb_config: MongoDbConfig
    model_config = SettingsConfigDict(env_prefix="CHAK_", case_sensitive=False)


settings = Settings()
