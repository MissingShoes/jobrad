"""A module to provide functionalities to manage chat sessions."""

from uuid import UUID, uuid4

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from chat_service.config import settings
from chat_service.model.chat import ChatMessage
from chat_service.schema import AuthorType
from chat_service.transport import ChatSessionResponse


class SessionNotFoundError(Exception):
    def __init__(self, session_id: UUID) -> None:
        super().__init__(f"Session {session_id} not found")


class ChatSessionManager:
    """
    A chat session manager class that acts as a helper to create and retrieve chat sessions and to send messages to it.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_new_session(self) -> ChatSessionResponse:
        """Create a new chat session by creating the initial default message."""
        new_session_id = uuid4()
        first_message = ChatMessage(
            id=uuid4(),
            session_id=new_session_id,
            content=settings.default_message,
            author_type=AuthorType.SERVICE_AGENT,
        )
        self.session.add(first_message)

        await self.session.flush()

        return await self.get_session(new_session_id)

    async def add_message_to_session(
        self, session_id: UUID, message_content: str, author_type: AuthorType
    ) -> ChatSessionResponse:
        """
        Add a message to an existing session.

        This will fail with a SessionNotFoundError if the session does not exist.
        """
        exists_query = select(1).where(
            exists().where(ChatMessage.session_id == session_id)
        )
        if not (await self.session.scalar(exists_query)):
            raise SessionNotFoundError(session_id)

        new_message = ChatMessage(
            id=uuid4(),
            session_id=session_id,
            content=message_content,
            author_type=author_type,
        )
        self.session.add(new_message)

        await self.session.flush()

        return await self.get_session(session_id)

    async def get_session(self, session_id: UUID) -> ChatSessionResponse:
        """
        Get a chat session by session id

        This will fail with a SessionNotFoundError if the session does not exist.
        ."""
        query = select(ChatMessage).where(ChatMessage.session_id == session_id)
        result = await self.session.scalars(query)
        messages = result.all()
        if not messages:
            raise SessionNotFoundError(session_id)
        return ChatSessionResponse.from_chat_messages(messages)
