from pydantic import BaseSettings


class Settings(BaseSettings):
    API_KEY: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"
