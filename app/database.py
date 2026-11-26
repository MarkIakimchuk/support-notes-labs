from collections.abc import Iterator
from secrets import token_urlsafe
from typing import Annotated

from fastapi import Depends
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://support:local-support-password@localhost:5432/support"
    jwt_secret: str = Field(default_factory=lambda: token_urlsafe(48), min_length=32)


class Base(DeclarativeBase):
    pass


settings = Settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
session_factory = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    with session_factory() as session:
        yield session


Database = Annotated[Session, Depends(get_db)]
