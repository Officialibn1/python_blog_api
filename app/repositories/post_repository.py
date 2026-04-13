import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.db import PostDB

class PostRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _slugify(self, title: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

    async def create(
        self,
        title: str,
        content: str,
        category_id: int,
        published: bool = False
    ) -> PostDB:
        post = PostDB(
            title=title,
            slug=self._slugify(title),
            content=content,
            category_id=category_id,
            published=published
        )

        self.db.add(post)
        await self.db.flush()
        await self.db.refresh(post)

        return post

    async def get_by_id(self, post_id: int) -> PostDB | None:
        result = await self.db.execute(select(PostDB).where(PostDB.id == post_id))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        published_only: bool,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[PostDB], int]:
        query = select(PostDB)

        if published_only:
            query = query.where(PostDB.published == True)

        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()
        result = await self.db.execute(query.limit(limit).offset(skip))

        return list(result.scalars().all()), total

    async def update(self, post_id: int, **fields) -> PostDB | None:
        post = await self.get_by_id(post_id)
        if not post:
            return None

        for key, value in fields.items():
            setattr(post, key, value)

        await self.db.flush()
        await self.db.refresh(post)

        return post

    async def delete(self, post_id: int) -> bool:
        post = await self.get_by_id(post_id)
        if not post:
            return False

        await self.db.delete(post)
        return True
