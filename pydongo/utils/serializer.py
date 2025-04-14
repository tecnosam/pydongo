import datetime

from typing import Any, Mapping, TypeVar
from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class BaseTypeSerializer(ABC):
    @staticmethod
    @abstractmethod
    def serialize(value: Any) -> Any: ...

    @staticmethod
    @abstractmethod
    def deserialize(value: Any) -> Any: ...


class DateSerializer(BaseTypeSerializer):
    @staticmethod
    def serialize(value: datetime.date) -> datetime.datetime:
        return datetime.datetime.combine(value, datetime.datetime.min.time())

    @staticmethod
    def deserialize(value: datetime.datetime) -> datetime.date:
        return value.date()


class UUIDSerializer(BaseTypeSerializer):
    @staticmethod
    def serialize(value: UUID) -> str:
        return str(value)

    @staticmethod
    def deserialize(value: str) -> UUID:
        return UUID(value)


HANDLER_MAPPING: Mapping[Any, BaseTypeSerializer] = {
    datetime.date: DateSerializer(),
    UUID: UUIDSerializer(),
}


def replace_unserializable_fields(document: dict) -> dict:
    def serialize(val: Any) -> Any:
        value_type = type(val)
        if value_type in HANDLER_MAPPING:
            val = HANDLER_MAPPING[value_type].serialize(val)
        return val

    for key, value in document.items():
        if isinstance(value, dict):
            document[key] = replace_unserializable_fields(value)
        elif isinstance(value, (list, tuple, set)):
            document[key] = [serialize(element) for element in value]
        else:
            document[key] = serialize(value)

    return document


def restore_unserializable_fields(document: dict) -> dict:
    # todo: this approach is logically incorrect
    # todo: We should bind this function to the field of the pydantic objects themselves
    # todo: food for thought: is providing this feature a form of over engineering or is it
    # todo: important for DX (developer experience)
    def deserialize(val: Any) -> Any:
        value_type = type(val)
        if value_type in HANDLER_MAPPING:
            val = HANDLER_MAPPING[value_type].deserialize(val)
        return val

    for key, value in document.items():
        if isinstance(value, dict):
            document[key] = restore_unserializable_fields(value)
        elif isinstance(value, (list, tuple, set)):
            document[key] = [deserialize(element) for element in value]
        else:
            document[key] = deserialize(value)

    return document
