import datetime
import uuid

from pydongo.utils.serializer import (
    replace_unserializable_fields,
    restore_unserializable_fields,
    HANDLER_MAPPING,
)

def test_date_serialization():
    today = datetime.date.today()
    document = {"created_at": today}
    serialized = replace_unserializable_fields(document.copy())

    assert isinstance(serialized["created_at"], datetime.datetime)
    assert serialized["created_at"].date() == today


def test_uuid_serialization():
    test_uuid = uuid.uuid4()
    document = {"id": test_uuid}
    serialized = replace_unserializable_fields(document.copy())

    assert isinstance(serialized["id"], str)
    assert serialized["id"] == str(test_uuid)


def test_nested_serialization():
    data = {
        "meta": {
            "created_at": datetime.date.today(),
            "uuid": uuid.uuid4(),
        },
        "tags": [uuid.uuid4(), uuid.uuid4()]
    }

    serialized = replace_unserializable_fields(data.copy())
    assert isinstance(serialized["meta"]["created_at"], datetime.datetime)
    assert all(isinstance(t, str) for t in serialized["tags"])
