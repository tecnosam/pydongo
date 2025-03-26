from typing import TypeVar, Optional
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


def as_document(pydantic_object: T) -> "DocumentWorker":
    return DocumentWorker(pydantic_object=pydantic_object)


class SaveResponse(BaseModel):
    inserted_id: Optional[str] = None
    modified_id: Optional[str] = None


class DeleteResponse(BaseModel):
    delete_count: int = 0


class DocumentWorker:
    def __init__(self, pydantic_object: T):
        self.pydantic_object = pydantic_object

    def save(self) -> SaveResponse:
        return SaveResponse()

    def delete(self) -> DeleteResponse:
        return DeleteResponse()
