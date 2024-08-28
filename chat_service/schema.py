"""Shared internal data types."""

from enum import StrEnum, auto


class AuthorType(StrEnum):
    """An enum to indicate whether the auther of a message was a customer or a service agent."""

    CUSTOMER = auto()
    SERVICE_AGENT = auto()
