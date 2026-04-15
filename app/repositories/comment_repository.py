from sqlalchemy import select
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

    async def get_by_post(self, post_id: int) -> list[CommentDB]:
        result = await self.db.execute(select(CommentDB).where(CommentDB.post_id == post_id))
        return list(result.scalars().all())

    async def delete(self, comment_id: int) -> bool:
        result = await self.db.execute(select(CommentDB).where(CommentDB.id == comment_id))
        comment = result.scalar_one_or_none()

        if not comment:
            raise NotFoundException(f"Comment with this id {comment_id} not found")

        await self.db.delete(comment)
        return True
