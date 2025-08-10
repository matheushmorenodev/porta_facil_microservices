# -----------------------------------------------------------------------------
# ARQUIVO: database.py
# DESCRIÇÃO: Configuração da conexão com o banco de dados usando SQLAlchemy.
# -----------------------------------------------------------------------------
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # O valor será lido do arquivo .env
    DATABASE_URL: str = "sqlite:///./log.db"

    class Config:
        env_file = ".env"

settings = Settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()