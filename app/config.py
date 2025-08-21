from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

ENV_PATH = BASE_DIR / ".env"





class BaseEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra="ignore")
    
    
    
class DataBaseSettings(BaseEnvSettings):    
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str 
    DATABASE_HOST: str 
    DATABASE_PORT: str
    echo: bool = True

class JwtSettings(BaseSettings):
    private_key: Path = BASE_DIR / "certs" / "private.pem"
    public_key: Path = BASE_DIR / "certs" / "public.pem"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1000


database_settings = DataBaseSettings() # type: ignore
settings = JwtSettings()

DB_URL = f"postgresql+asyncpg://{database_settings.DATABASE_USER}:{database_settings.DATABASE_PASSWORD}@{database_settings.DATABASE_HOST}:{database_settings.DATABASE_PORT}/{database_settings.DATABASE_NAME}"

