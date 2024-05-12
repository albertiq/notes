from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    web_port: int = Field(8000)


settings = AppSettings()
