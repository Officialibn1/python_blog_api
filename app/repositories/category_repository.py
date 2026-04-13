import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.db import CategoryDB, TagDB

class CategoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _sluggify(self, name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    async def create(self, name: str) -> CategoryDB:
        category = CategoryDB(
            name=name,
            slug=self._sluggify(name)
        )
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def get_by_id(self, category_id: int) -> CategoryDB | None:
        result = await self.db.execute(
            select(CategoryDB).where(CategoryDB.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[CategoryDB]:
        result = await self.db.execute(
            select(CategoryDB)
        )
        return list(result.scalars().all())

    async def delete(self, category_id: int) -> bool:
        category = await self.get_by_id(category_id)
        if not category:
            return False

        await self.db.delete(category)
        return True



class TagRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _sluggify(self, name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    async def create(self, name: str) -> TagDB:
        tag = TagDB(
            name=name,
            slug=self._sluggify(name)
        )

        self.db.add(tag)
        await self.db.flush()
        await self.db.refresh(tag)
        return tag

    async def get_by_id(self, tag_id: int) -> TagDB | None:
        result = await self.db.execute(select(TagDB).where(TagDB.id == tag_id))

        return result.scalar_one_or_none()

    async def get_all(self) -> list[TagDB]:
        result = await self.db.execute(select(TagDB))

        return list(result.scalars().all())

    async def delete(self, tag_id: int) -> bool:
        tag = self.get_by_id(tag_id)
        if not tag:
            return False

        await self.db.delete(tag)
        return True
