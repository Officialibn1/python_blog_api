from pydantic import BaseModel, field_validator

from .common import NonBlankString


class TagBase(BaseModel):
    name: NonBlankString

    @field_validator("name")
    @classmethod
    def capitalize_name(cls, v: str) -> str:
        return v.title()

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    slug: str

    model_config = {"from_attributes": True}
