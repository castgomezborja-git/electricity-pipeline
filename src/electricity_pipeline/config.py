from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    ree_api_base_url: str = "https://apidatos.ree.es/es/datos"