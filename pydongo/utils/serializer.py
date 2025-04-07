import datetime

from typing import Any, Mapping, TypeVar
from abc import ABC, abstractmethod

from pydantic import BaseModel

from pydongo.models.serializable_types import Datetime


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


HANDLER_MAPPING: Mapping[Any, BaseTypeSerializer] = {datetime.date: DateSerializer()}


def replace_unserializable_fields(pydantic_object: T) -> T:
    for field_name in pydantic_object.__class__.model_fields.keys():
        value = getattr(pydantic_object, field_name)
        value_type = type(value)

        if value_type in HANDLER_MAPPING:
            handler = HANDLER_MAPPING[value_type]
            setattr(pydantic_object, field_name, handler.serialize(value))

        if issubclass(value_type.__class__, BaseModel):
            setattr(pydantic_object, field_name, replace_unserializable_fields(value))

    return pydantic_object


def restore_unserializable_fields(document: dict) -> dict:
    def deserialize(val: Any) -> Any:
        value_type = type(val)
        if value_type in HANDLER_MAPPING:
            val = HANDLER_MAPPING[value_type].deserialize(val)
        return val

    for key, value in document:
        if isinstance(value, dict):
            document[key] = restore_unserializable_fields(value)
        elif isinstance(value, (list, tuple, set)):
            document[key] = [deserialize(element) for element in value]
        else:
            document[key] = deserialize(value)

    return document
