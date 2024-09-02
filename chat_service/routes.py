"""The API endpoints for interacting with chat sessions."""

from http import HTTPStatus
from typing import Literal
from uuid import UUID

from quart import Blueprint
from quart_schema import tag, validate_request, validate_response
from werkzeug.exceptions import BadRequest, NotFound

from chat_service.model import async_session
from chat_service.services import ChatSessionManager, SessionNotFoundError, SessionResolvedError
from chat_service.transport import ChatSessionResponse, PostMessageRequest, UnresolvedSessionsResponse

bp = Blueprint("messages", __name__)


@tag(["Chat"])
@bp.post("/sessions")
@validate_response(ChatSessionResponse)
async def create_session() -> tuple[ChatSessionResponse, Literal[HTTPStatus.CREATED]]:
    """Create a new chat session."""
    async with async_session.begin() as session:
        chat_session_manager = ChatSessionManager(session)
        chat_session = await chat_session_manager.create_new_session()

        return chat_session, HTTPStatus.CREATED


@tag(["Chat"])
@bp.get("/sessions/<uuid:session_id>")
@validate_response(ChatSessionResponse)
async def get_session(session_id: UUID) -> ChatSessionResponse:
    """Retrieve an existing chat session with all its messages."""
    async with async_session.begin() as session:
        chat_session_manager = ChatSessionManager(session)
        try:
            return await chat_session_manager.get_session(session_id)
        except SessionNotFoundError:
            raise NotFound(f"Session {session_id} not found")


@tag(["Chat"])
@bp.post("/sessions/<uuid:session_id>/messages")
@validate_request(PostMessageRequest)
@validate_response(ChatSessionResponse)
async def send_message(
    session_id: UUID, data: PostMessageRequest
) -> tuple[ChatSessionResponse, Literal[HTTPStatus.CREATED]]:
    """Send a message to a chat session.

    This will return the whole session with all its messages.
    """
    async with async_session.begin() as session:
        chat_session_manager = ChatSessionManager(session)
        try:
            chat_session = await chat_session_manager.add_message_to_session(
                session_id=session_id,
                message_content=data.content,
                author_type=data.author_type,
                is_resolution=data.is_resolution,
            )
        except SessionNotFoundError:
            raise NotFound(f"Session {session_id} was not found.")
        except SessionResolvedError:
            raise BadRequest("Cannot send message to a resolved chat.")

        return chat_session, HTTPStatus.CREATED


@tag(["Chat"])
@bp.get("/sessions/unresolved")
@validate_response(UnresolvedSessionsResponse)
async def get_unresolved_sessions() -> UnresolvedSessionsResponse:
    """Retrieve all unresolved chat sessions."""
    async with async_session.begin() as session:
        chat_session_manager = ChatSessionManager(session)
        unresolved_sessions = await chat_session_manager.get_unresolved_sessions()
        return UnresolvedSessionsResponse(sessions=unresolved_sessions)
