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
        exist = await self.get_by_name(name)
        if exist:
            raise ConflictException("Category with this name already exists")

        category = CategoryDB(
            name=name,
            slug=self._sluggify(name)
        )
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def update(self, category_id: int, name: str) -> CategoryDB:
        category = await self.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category with this id does not exist")

        check = await self.get_by_name(name)
        if check:
            raise ConflictException("Category with this name already exist")

        category.name = name
        category.slug = self._sluggify(name)

        await self.db.flush()
        await self.db.refresh(category)
        return category


    async def get_by_id(self, category_id: int) -> CategoryDB | None:
        result = await self.db.execute(
            select(CategoryDB).where(CategoryDB.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> CategoryDB | None:
        query = select(CategoryDB).where(CategoryDB.name == name)
        result = await self.db.execute(query)
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
        exist = await self.get_by_name(name)
        if exist:
            raise ConflictException("Tag with this name already exist")

        tag = TagDB(
            name=name,
            slug=self._sluggify(name)
        )

        self.db.add(tag)
        await self.db.flush()
        await self.db.refresh(tag)
        return tag

    async def update(self, tag_id: int, name: str) -> TagDB:
        tag = await self.get_by_id(tag_id)
        if not tag:
            raise NotFoundException("Tag not found")

        check = await self.get_by_name(name)
        if check:
            raise ConflictException("Tag with this name already exist")

        tag.name = name
        tag.slug = self._sluggify(name)
        await self.db.flush()
        await self.db.refresh(tag)
        return tag

    async def get_by_id(self, tag_id: int) -> TagDB | None:
        result = await self.db.execute(select(TagDB).where(TagDB.id == tag_id))

        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> TagDB | None:
        query = select(TagDB).where(TagDB.name == name)
        result = await self.db.execute(query)
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
