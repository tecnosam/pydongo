from abc import ABC
from abc import abstractmethod
from typing import Any


class BaseExpression(ABC):
    """Base class for all MongoDB expressions."""

    @abstractmethod
    def serialize(self) -> Any:
        """Serialize an expression into a MongoDB compatible query DTO."""
