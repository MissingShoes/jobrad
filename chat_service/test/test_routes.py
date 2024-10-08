from http import HTTPStatus
from typing import Callable, Iterator
from unittest.mock import ANY, Mock
from uuid import UUID

import pytest
from alembic.command import downgrade, upgrade
from alembic.config import Config
from pytest_mock import MockerFixture
from quart import Quart
from quart.testing import QuartClient

from chat_service.app import create_app


@pytest.fixture
def app() -> Quart:
    app = create_app()
    return app


@pytest.fixture
def client(app: Quart) -> QuartClient:
    return app.test_client()  # type: ignore


@pytest.fixture(autouse=True)
def migrated_db() -> Iterator[None]:
    """Apply all migrations to the database"""
    alembic_config = Config(file_="alembic.ini")
    downgrade(alembic_config, "base")
    upgrade(alembic_config, "head")
    yield
    downgrade(alembic_config, "base")


@pytest.fixture()
def mock_uuid(mocker: MockerFixture) -> Mock:
    mock = mocker.patch("chat_service.services.uuid4", autospec=True)

    def get_auto_incrementing_uuid() -> Callable[[], UUID]:
        current = 0

        def auto_incrementing_uuid() -> UUID:
            nonlocal current
            new_id = UUID(f"00000000-0000-0000-0000-{current:012d}")
            current += 1
            return new_id

        return auto_incrementing_uuid

    mock.side_effect = get_auto_incrementing_uuid()
    return mock


async def test_health_check(client: QuartClient) -> None:
    response = await client.get("/health")
    assert response.status_code == HTTPStatus.OK


async def test_creating_a_session_returns_a_session_with_a_default_message(
    client: QuartClient, mock_uuid: Mock
) -> None:
    response = await client.post("/sessions")

    assert response.status_code == HTTPStatus.CREATED
    response_json = await response.json
    assert response_json == {
        "created_at": ANY,
        "id": "00000000-0000-0000-0000-000000000000",
        "messages": [
            {
                "author_type": "service_agent",
                "content": "Hello, how may I help you?",
                "timestamp": ANY,
            }
        ],
    }
    # assert session creation time is timestamp of first message instead of trying to mock the server side timestamp
    assert response_json["created_at"] == response_json["messages"][0]["timestamp"]


async def test_sending_multiple_messages(client: QuartClient, mock_uuid: Mock) -> None:
    response = await client.post("/sessions")
    assert response.status_code == HTTPStatus.CREATED

    first_message_response = await client.post(
        "/sessions/00000000-0000-0000-0000-000000000000/messages",
        json={"content": "I have an issue.", "author_type": "customer"},
    )
    assert first_message_response.status_code == HTTPStatus.CREATED

    session_after_first_message = await first_message_response.json
    assert len(session_after_first_message["messages"]) == 2
    assert session_after_first_message["messages"][-1]["content"] == "I have an issue."
    assert session_after_first_message["messages"][-1]["author_type"] == "customer"

    second_message_response = await client.post(
        "/sessions/00000000-0000-0000-0000-000000000000/messages",
        json={"content": "I am sorry to hear that.", "author_type": "service_agent"},
    )
    assert second_message_response.status_code == HTTPStatus.CREATED

    session_after_second_message = await second_message_response.json
    assert len(session_after_second_message["messages"]) == 3
    assert (
        session_after_second_message["messages"][-1]["content"]
        == "I am sorry to hear that."
    )
    assert (
        session_after_second_message["messages"][-1]["author_type"] == "service_agent"
    )


async def test_sending_a_message_to_an_inexistent_session_yields_a_404(
    client: QuartClient,
) -> None:
    first_message_response = await client.post(
        "/sessions/00000000-0000-0000-0000-000000000000/messages",
        json={"content": "I have an issue.", "author_type": "customer"},
    )
    assert first_message_response.status_code == HTTPStatus.NOT_FOUND


async def test_retrieve_existing_session_by_id(
    client: QuartClient, mock_uuid: Mock
) -> None:

    # create a session with a default message
    creation_response = await client.post("/sessions")
    assert creation_response.status_code == HTTPStatus.CREATED

    first_retrieval_response = await client.get(
        "/sessions/00000000-0000-0000-0000-000000000000"
    )
    assert first_retrieval_response.status_code == HTTPStatus.OK
    assert (await first_retrieval_response.json) == {
        "created_at": ANY,
        "id": "00000000-0000-0000-0000-000000000000",
        "messages": [
            {
                "author_type": "service_agent",
                "content": "Hello, how may I help you?",
                "timestamp": ANY,
            }
        ],
    }

    # add another message
    await client.post(
        "/sessions/00000000-0000-0000-0000-000000000000/messages",
        json={
            "content": "I have an issue.",
            "author_type": "customer",
        },
    )

    # ...and ensure that it is included in the response
    second_retrieval_response = await client.get(
        "/sessions/00000000-0000-0000-0000-000000000000"
    )
    assert second_retrieval_response.status_code == HTTPStatus.OK
    assert (await second_retrieval_response.json) == {
        "created_at": ANY,
        "id": "00000000-0000-0000-0000-000000000000",
        "messages": [
            {
                "author_type": "service_agent",
                "content": "Hello, how may I help you?",
                "timestamp": ANY,
            },
            {
                "author_type": "customer",
                "content": "I have an issue.",
                "timestamp": ANY,
            },
        ],
    }


async def test_retrieving_an_inexistent_session_yields_a_404(
    client: QuartClient, mock_uuid: Mock
) -> None:
    response = await client.get("/sessions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == HTTPStatus.NOT_FOUND
