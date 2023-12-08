from pydantic import Field, Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    auth_key: str = Field(validation_alias="my_auth_key")
    default_models: Path = Field(alias="my_api_key")
