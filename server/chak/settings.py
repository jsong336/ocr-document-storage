from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


class MongoDbConfig(BaseModel):
    connection_uri: str
    database: str


class GoogleCloudConfig(BaseModel):
    oauth_client_credential: str


class Settings(BaseSettings):
    mongodb_config: MongoDbConfig
    google_cloud_config: GoogleCloudConfig
    session_secret_key: str

    model_config = SettingsConfigDict(env_prefix="CHAK_", case_sensitive=False)


settings = Settings()
