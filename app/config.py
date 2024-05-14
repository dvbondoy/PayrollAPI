from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    database_port: str
    database_name: str
    database_password: str
    database_username: str
    secret_key: str
    algorithm: str
    token_expiration: int

    class Config:
        env_file = ".env"

settings = Settings()