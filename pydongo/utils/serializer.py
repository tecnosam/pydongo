import datetime

from typing import Any, Mapping, TypeVar
from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class BaseTypeSerializer(ABC):
    """
    Abstract base class for type serializers.

    Implementations define how to convert values to and from MongoDB-compatible types.
    """

    @staticmethod
    @abstractmethod
    def serialize(value: Any) -> Any:
        """
        Convert a Python value into a MongoDB-storable format.

        Args:
            value (Any): The value to serialize.

        Returns:
            Any: A serialized version of the value.
        """

    @staticmethod
    @abstractmethod
    def deserialize(value: Any) -> Any:
        """
        Convert a MongoDB-stored value back to a Python-native type.

        Args:
            value (Any): The value to deserialize.

        Returns:
            Any: The original Python representation.
        """


class DateSerializer(BaseTypeSerializer):
    """
    Serializer for converting `datetime.date` to `datetime.datetime`.

    Ensures compatibility with MongoDB, which only supports datetime objects.
    """

    @staticmethod
    def serialize(value: datetime.date) -> datetime.datetime:
        """
        Serialize a `date` object into a UTC `datetime` object.

        Args:
            value (datetime.date): The date to serialize.

        Returns:
            datetime.datetime: A datetime object representing midnight of the same date.
        """
        return datetime.datetime.combine(value, datetime.datetime.min.time())

    @staticmethod
    def deserialize(value: datetime.datetime) -> datetime.date:
        """
        Deserialize a `datetime` object back into a `date`.

        Args:
            value (datetime.datetime): The datetime to convert.

        Returns:
            datetime.date: The date component of the datetime.
        """
        return value.date()


class UUIDSerializer(BaseTypeSerializer):
    """
    Serializer for UUIDs, converting them to and from strings.
    """

    @staticmethod
    def serialize(value: UUID) -> str:
        """
        Convert a UUID to a string for MongoDB storage.

        Args:
            value (UUID): The UUID to serialize.

        Returns:
            str: String representation of the UUID.
        """
        return str(value)

    @staticmethod
    def deserialize(value: str) -> UUID:
        """
        Convert a string back into a UUID object.

        Args:
            value (str): UUID string.

        Returns:
            UUID: The corresponding UUID object.
        """
        return UUID(value)


HANDLER_MAPPING: Mapping[Any, BaseTypeSerializer] = {
    datetime.date: DateSerializer(),
    UUID: UUIDSerializer(),
}


def replace_unserializable_fields(document: dict) -> dict:
    """
    Recursively replaces values in a document that are not MongoDB-compatible
    with serialized equivalents, using registered type handlers.

    Args:
        document (dict): The original document to sanitize.

    Returns:
        dict: A deep-copied document with serializable values.
    """

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
    """
    Recursively attempts to deserialize known types in a document.

    NOTE: This is a basic placeholder strategy — it applies all registered deserializers
    without knowing the intended field type. This can result in incorrect types.

    It's recommended to use field-aware deserialization (tied to model schemas)
    for production use.

    Args:
        document (dict): A document retrieved from MongoDB.

    Returns:
        dict: A deep-copied document with deserialized values (best-effort).
    """

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
