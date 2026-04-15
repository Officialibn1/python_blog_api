import re
from enum import EnumType
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import ConflictException, NotFoundException
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

    async def delete(self, category_id: int) -> None:
        category = await self.get_by_id(category_id)
        if not category:
            raise NotFoundException(f"Category with this id {category_id} not found.")

        try:
            await self.db.delete(category)
            await self.db.flush()

        except IntegrityError:
            await self.db.rollback()
            raise ConflictException(f"Category with this id {category_id} is linked to a post and cannot be deleted.")


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

    async def delete(self, tag_id: int) -> None:
        tag = await self.get_by_id(tag_id)
        if not tag:
            raise NotFoundException(f"Tag with this id {tag_id} not found")

        try:
            await self.db.delete(tag)
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise ConflictException(f"Tag with this id {tag_id} is in use and cannot be deleted.")
