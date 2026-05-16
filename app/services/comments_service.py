from app.repositories.comment_repository import CommentRepository
from app.models.db import CommentDB
from app.schemas.comment import CommentCreate
from app.core.exceptions import NotFoundException

class CommentService:
    def __init__(self, comment_repo: CommentRepository) -> None:
        self.comment_repo = comment_repo

    async def create(self, data: CommentCreate, author_name: str) -> CommentDB:
        comment = await self.comment_repo.create(
            post_id=data.post_id,
            author_name=author_name,
            body=data.body
        )

        return comment

    async def get_post_comments(self, post_id: int) -> list[CommentDB]:
        return await self.comment_repo.get_by_post(post_id)

    async def get_comment(self, comment_id: int) -> CommentDB:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundException("Comment with this id not found")

        return comment

    async def edit_comment(self, comment_id: int, body: str) -> CommentDB:
        return await self.comment_repo.edit_comment(comment_id, body)

    async def delete_comment(self, comment_id: int) -> None:
        await self.comment_repo.delete(comment_id)
