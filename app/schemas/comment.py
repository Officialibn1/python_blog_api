from pydantic import BaseModel, field_validator
from .common import NonBlankString

class CommentBase(BaseModel):
    author_name: NonBlankString
    body: NonBlankString
    post_id: int

    @field_validator("author_name")
    @classmethod
    def cappitalize_author_name(cls, v: str) -> str:
        return v.title()

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int


    model_config = {"from_attributes": True}
