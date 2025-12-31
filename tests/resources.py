"""Data models for testing purposes."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Friend(BaseModel):
    """A simple friend model."""

    username: str
    age: int


class DemoModel(BaseModel):
    """A demo model."""

    name: str
    email: str
    bio: str
    hash_id: str
    latlon: list[float] = Field(default_factory=lambda: [0.0, 0.0])
    point: dict[str, Any] = Field(default_factory=lambda: {"type": "Point", "coordinates": [0.0, 0.0]})


class AsyncDemoModel(BaseModel):
    """An asynchronous demo model."""

    name: str
    email: str
    bio: str
    hash_id: str
    latlon: list[float] = Field(default_factory=lambda: [0.0, 0.0])
    point: dict[str, Any] = Field(default_factory=lambda: {"type": "Point", "coordinates": [0.0, 0.0]})


class User(BaseModel):
    """A user model with basic fields."""

    name: str = "John Doe"
    age: int = 19
    joined: int = 2023
    n_likes: int = 0
    close_friend: Friend = Friend(username="XXXXXX", age=20)
    best_friend: Friend = Friend(username="YYYYYY", age=21)


class UserWithModelConfig(BaseModel):
    """A user model with custom model configuration."""

    age: int = 19
    n_likes: int = 0

    model_config = ConfigDict(collection_name="customusers")  # type: ignore  # noqa: PGH003


class DummyModel(BaseModel):
    """A dummy model for testing purposes."""

    name: str
    age: int
    tags: list[str]
    friends: list[Friend]
    bff: Friend
