from pydantic.types import StringConstraints
from pydantic import BaseModel
from typing import Annotated, Generic, TypeVar

NonBlankString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
