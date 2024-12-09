"""The request and response models as expected and returned by the API."""

from __future__ import annotations

from datetime import datetime
from operator import attrgetter
from typing import Iterable
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from chat_service.model.chat import ChatMessage
from chat_service.schema import AuthorType

# request models


class PostMessageRequest(BaseModel):
    """The request model for a"""

    author_type: AuthorType = Field(
        description="The type of the author of the message."
    )
    content: str = Field(description="The content of the message.")
    is_resolution: bool = Field(
        description="Whether or not the message is a resolution message that resolves the session.",
        default=False,
    )


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

    session_id: UUID = Field(
        description="The session ID of the chat session.", exclude=True
    )
    is_resolution: bool = Field(
        description="Whether the message resolves the the chat session.", exclude=True
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
    def from_chat_messages(cls, messages: Iterable[ChatMessage]) -> ChatSessionResponse:
        """Instantiate a session response from a list of chat messages. This will fail if no messages are provided."""
        if not messages:
            raise ValueError("No messages received")

        message_responses = sorted(
            (MessageResponse.model_validate(m) for m in messages),
            key=attrgetter("timestamp"),
        )

        return cls(
            id=message_responses[0].session_id,
            created_at=message_responses[0].timestamp,
            messages=message_responses,
        )

    def add_message(self, message: ChatMessage) -> None:
        """Add a chat message to the messages in this session."""
        new_message = MessageResponse.model_validate(message)
        self.messages = sorted(
            self.messages + [new_message], key=attrgetter("timestamp")
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_resolved(self) -> bool:
        """Whether the chat session has been resolved or not."""
        return any(m.is_resolution for m in self.messages)


class UnresolvedSessionsResponse(BaseModel):
    """A collection of unresolved sessions."""

    sessions: list[ChatSessionResponse]
