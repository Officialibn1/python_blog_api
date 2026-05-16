from pydantic import BaseModel, field_validator

from .common import NonBlankString

class CategoryBase(BaseModel):
    name: NonBlankString

    @field_validator("name")
    @classmethod
    def capitalize_name(cls, v: str) -> str:
        return v.title()

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    slug: str

    model_config = {"from_attributes": True}
