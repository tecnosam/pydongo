"""Test serializer utils."""

import datetime
import uuid

from pydongo.utils.serializer import replace_unserializable_fields


def test_date_serialization(current_date: datetime.date) -> None:
    """Test serialization of datetime.date."""
    document = {"created_at": current_date}
    serialized = replace_unserializable_fields(document.copy())

    assert isinstance(serialized["created_at"], datetime.datetime)
    assert serialized["created_at"].date() == current_date


def test_uuid_serialization() -> None:
    """Test serialization of UUID fields."""
    test_uuid = uuid.uuid4()
    document = {"id": test_uuid}
    serialized = replace_unserializable_fields(document.copy())

    assert isinstance(serialized["id"], str)
    assert serialized["id"] == str(test_uuid)


def test_nested_serialization(current_date: datetime.date) -> None:
    """Test serialization of nested fields with datetime and UUID."""
    data = {
        "meta": {
            "created_at": current_date,
            "uuid": uuid.uuid4(),
        },
        "tags": [uuid.uuid4(), uuid.uuid4()],
    }

    serialized = replace_unserializable_fields(data.copy())
    assert isinstance(serialized["meta"]["created_at"], datetime.datetime)
    assert all(isinstance(t, str) for t in serialized["tags"])
