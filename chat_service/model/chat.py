"""The data model for the chat messages."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from chat_service.schema import AuthorType


class Base(DeclarativeBase):
    pass


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    content: Mapped[str]
    author_type: Mapped[AuthorType] = mapped_column(SQLAlchemyEnum(AuthorType))
    is_resolution: Mapped[bool] = mapped_column(default=False)

    session_id: Mapped[UUID]
