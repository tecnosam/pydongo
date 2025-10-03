"""Test resolving annotations."""

from typing import Annotated
from typing import Optional
from typing import Union

from src.pydongo.utils.annotations import resolve_annotation


def test_resolve_annotation_union() -> None:
    """Test resolving Union annotations."""
    assert resolve_annotation(Union[int, str]) is int
    assert resolve_annotation(Union[None, float]) is float
    assert resolve_annotation(Union[float, None]) is float


def test_resolve_annotation_optional() -> None:
    """Test resolving Optional annotations."""
    assert resolve_annotation(Optional[str]) is str
    assert resolve_annotation(Optional[Union[str, None]]) is str


def test_resolve_annotation_annotated() -> None:
    """Test resolving Annotated annotations."""
    assert resolve_annotation(Annotated[int, "meta"]) is int
    assert resolve_annotation(Annotated[Optional[int], "meta"]) is int
