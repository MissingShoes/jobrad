"""The request and response models as expected and returned by the API."""

from __future__ import annotations

from datetime import datetime
from operator import attrgetter
from typing import Sequence
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from chat_service.model.chat import ChatMessage
from chat_service.schema import AuthorType

# request models


class PostMessageRequest(BaseModel):
    """The request model for a"""

    author_type: AuthorType = Field(
        description="The type of the author of the message."
    )
    content: str = Field(description="The content of the message.")


# response models


class _ResponseBaseModel(BaseModel):
    """A base model for all API responses."""

    model_config = ConfigDict(
        from_attributes=True
    )  # allows direct parsing from (ORM) objects


class MessageResponse(_ResponseBaseModel):
    timestamp: datetime = Field(
        description="The server side timestamp of the message creation."
    )
    content: str = Field(description="The content of the message.")
    author_type: AuthorType = Field(
        description="The type of the author of the message."
    )


class ChatSessionResponse(_ResponseBaseModel):
    id: UUID
    created_at: datetime = Field(
        description="The server side timestamp of the session creation. "
        "This equals the creation timestamp of the first message."
    )
    messages: list[MessageResponse] = Field(
        description="The messages in the session in ascending chronological order."
    )

    @classmethod
    def from_chat_messages(cls, messages: Sequence[ChatMessage]) -> ChatSessionResponse:
        """Instantiate a session response from a list of chat messages. This will fail if no messages are provided."""
        if not messages:
            raise ValueError("No messages received")

        message_responses = sorted(
            (MessageResponse.model_validate(m) for m in messages),
            key=attrgetter("timestamp"),
        )
        return cls(
            id=messages[0].session_id,
            created_at=messages[0].timestamp,
            messages=message_responses,
        )

    def add_message(self, message: ChatMessage) -> None:
        """Add a chat message to the messages in this session."""
        new_message = MessageResponse.model_validate(message)
        self.messages = sorted(
            self.messages + [new_message], key=attrgetter("timestamp")
        )
