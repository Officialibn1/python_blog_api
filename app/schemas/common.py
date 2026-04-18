from pydantic import BaseModel
from typing import Annotated, Generic, TypeVar
from pydantic.types import StringConstraints

NonBlankString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
PasswordString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=8)]

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
