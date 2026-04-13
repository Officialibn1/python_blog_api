from fastapi import HTTPException, status
from app.repositories.comment_repository import CommentRepository
from app.models.domain import Comment
from app.schemas.comment import CommentCreate

class CommentService:
    def __init__(self, comment_repo: CommentRepository) -> None:
        self.comment_repo = comment_repo

    def create(self, data: CommentCreate) -> Comment:
        comment = self.comment_repo.create(
            post_id=data.post_id,
            author_name=data.author_name,
            body=data.body
        )

        return comment

    def get_post_comments(self, post_id: int) -> list[Comment]:
        return self.comment_repo.get_by_post(post_id)

    def delete_comment(self, comment_id: int) -> None:
        success = self.comment_repo.delete(comment_id)

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
