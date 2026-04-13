from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

from .category import CategoryResponse
from .tag import TagResponse
from .common import NonBlankString

class PostBase(BaseModel):
    title: NonBlankString
    content: NonBlankString
    category_id: int
    tag_ids: list[int] = []
    published: bool = False

    @field_validator("title", "content")
    @classmethod
    def capitalize_fields(cls, v: str) -> str:
        return v.title()

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: Optional[list[int]] = None
    published: Optional[bool] = None

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    category_id: int
    category: CategoryResponse
    published: bool
    tag_ids: list[int] = []
    tags: list[TagResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
