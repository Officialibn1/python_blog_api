from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.db import CommentDB

class CommentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, body: str, author_name: str, post_id: int) -> CommentDB:
        comment = CommentDB(
            body=body,
            author_name=author_name,
            post_id=post_id
        )

        self.db.add(comment)
        await self.db.flush()
        await self.db.refresh(comment)

        return comment

    async def get_by_post(
        self,
        post_id: int,
        skip: int,
        limit: int
    ) -> tuple[list[CommentDB], int]:
        query = select(CommentDB).where(CommentDB.post_id == post_id)
        count = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count.scalar_one()

        result = await self.db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_by_id(self, comment_id: int) -> CommentDB | None:
        query = select(CommentDB).where(CommentDB.id == comment_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def edit_comment(self, comment_id: int, body: str) -> CommentDB:
        comment = await self.get_by_id(comment_id)
        if not comment:
            raise NotFoundException("Comment not found")

        comment.body = body
        await self.db.flush()
        await self.db.refresh(comment)
        return comment

    async def delete(self, comment_id: int) -> bool:
        result = await self.db.execute(select(CommentDB).where(CommentDB.id == comment_id))
        comment = result.scalar_one_or_none()

        if not comment:
            raise NotFoundException(f"Comment with this id {comment_id} not found")

        await self.db.delete(comment)
        return True
