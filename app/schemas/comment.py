from pydantic import BaseModel
from .common import NonBlankString

class CommentBase(BaseModel):
    # author_name: NonBlankString
    body: NonBlankString
    post_id: int

    # @field_validator("author_name")
    # @classmethod
    # def cappitalize_author_name(cls, v: str) -> str:
    #     return v.title()

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    body: NonBlankString

class CommentResponse(CommentBase):
    id: int
    author_name: NonBlankString


    model_config = {"from_attributes": True}
