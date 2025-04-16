from typing import Annotated, Any, Optional, Union, get_args, get_origin


def resolve_annotation(annotation: Any) -> Any:
    """
    Helper function to resolve actual data types from Optional, Union, or Annotated wrappers.

    Args:
        annotation (Any): Type annotation from the Pydantic model.

    Returns:
        Any: The resolved base type annotation.
    """
    origin = get_origin(annotation)
    if origin is Union or origin is Optional:
        args = get_args(annotation)
        non_none_args = [arg for arg in args if arg is not type(None)]
        return resolve_annotation(non_none_args[0] if non_none_args else annotation)
    if origin is Annotated:
        annotation = resolve_annotation(get_args(annotation)[0])

    return annotation
