"""Initialisation and configuration of the database engine."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from chat_service.config import settings

engine = create_async_engine(settings.database.uri, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
