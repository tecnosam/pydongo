import datetime

from typing import TypeVar

from pydantic import BaseModel

from pydongo.models.serializable_types import Datetime


T = TypeVar("T", bound=BaseModel)


HANDLER_MAPPING = {
    datetime.date: lambda value: Datetime(
        original_type="datetime.date",
        value=datetime.datetime.combine(value, datetime.datetime.min.time()),
    )
}


def replace_unserializable_fields(pydantic_object: T) -> T:
    for field_name in pydantic_object.__class__.model_fields.keys():
        value = getattr(pydantic_object, field_name)
        value_type = type(value)

        if value_type in HANDLER_MAPPING:
            handler = HANDLER_MAPPING[value_type]
            setattr(pydantic_object, field_name, handler(value))

        if issubclass(value_type.__class__, BaseModel):
            setattr(pydantic_object, field_name, replace_unserializable_fields(value))

    return pydantic_object
