from typing import Annotated, Any, Optional, Union, get_args, get_origin


def resolve_annotation(annotation: Any) -> Any:
    """Helper function to resolve actual data types from Optional, Union, or Annotated wrappers.

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


# def resolve_annotation(annotation: Any) -> Any:
#     """Resolve the base type from Optional, Union, Annotated, and generic containers."""

#     while True:
#         origin = get_origin(annotation)

#         # Optional / Union[T, None]
#         if origin is Union:
#             args = [arg for arg in get_args(annotation) if arg is not type(None)]
#             annotation = args[0] if args else annotation
#             continue

#         # Annotated[T, ...]
#         if origin is Annotated:
#             annotation = get_args(annotation)[0]
#             continue

#         # Built-in generics: list[T], dict[K, V], set[T], tuple[T], etc.
#         if origin is not None:
#             args = get_args(annotation)
#             if args:
#                 # Prefer the "value" type for mappings
#                 annotation = args[-1]
#                 continue

#         break

#     return annotation
