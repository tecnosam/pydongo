from abc import ABC, abstractmethod
from typing import Any


class BaseExpression(ABC):
    @abstractmethod
    def serialize(self) -> Any:
        """
        Serialize an expression into a MongoDB compatible query DTO
        """
