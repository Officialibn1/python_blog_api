from fastapi import HTTPException, status
from app.repositories.comment_repository import CommentRepository
from app.models.db import CommentDB
from app.schemas.comment import CommentCreate

class CommentService:
    def __init__(self, comment_repo: CommentRepository) -> None:
        self.comment_repo = comment_repo

    async def create(self, data: CommentCreate) -> CommentDB:
        comment = await self.comment_repo.create(
            post_id=data.post_id,
            author_name=data.author_name,
            body=data.body
        )

        return comment

    async def get_post_comments(self, post_id: int) -> list[CommentDB]:
        return await self.comment_repo.get_by_post(post_id)

    async def delete_comment(self, comment_id: int) -> None:
        success = await self.comment_repo.delete(comment_id)

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
