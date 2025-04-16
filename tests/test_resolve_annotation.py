from typing import Annotated, Optional, Union
from pydongo.utils.annotations import resolve_annotation


def test_resolve_annotation_union():
    assert resolve_annotation(Union[int, str]) == int
    assert resolve_annotation(Union[None, float]) == float
    assert resolve_annotation(Union[float, None]) == float


def test_resolve_annotation_optional():
    assert resolve_annotation(Optional[str]) == str
    assert resolve_annotation(Optional[Union[str, None]]) == str


def test_resolve_annotation_annotated():
    assert resolve_annotation(Annotated[int, "meta"]) == int
    assert resolve_annotation(Annotated[Optional[int], "meta"]) == int
