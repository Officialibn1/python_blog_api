from app.core.exceptions import NotFoundException
from app.repositories.category_repository import CategoryRepository, TagRepository
from app.schemas.category import CategoryCreate
from app.schemas.tag import TagCreate
from app.models.db import CategoryDB, TagDB

class CategoryService:
    def __init__(self, category_repo: CategoryRepository) -> None:
        self.category_repo = category_repo

    async def create_category(self, data: CategoryCreate) -> CategoryDB:
        category = await self.category_repo.create(
            name=data.name
        )
        return category

    async def get_category(self, category_id: int) -> CategoryDB:
        category = await self.category_repo.get_by_id(category_id)
        if category is None:
            raise NotFoundException(f"Category with this id {category_id} not found")

        return category

    async def get_all(self) -> list[CategoryDB]:
        return await self.category_repo.get_all()

    async def delete_category(self, category_id: int) -> None:
        await self.category_repo.delete(category_id)

class TagService:
    def __init__(self, tag_repo: TagRepository) -> None:
        self.tag_repo = tag_repo

    async def create(self, data: TagCreate) -> TagDB:
        tag = await self.tag_repo.create(
            name=data.name
        )
        return tag

    async def get_tag(self, tag_id: int) -> TagDB:
        tag = await self.tag_repo.get_by_id(tag_id)
        if tag is None:
            raise NotFoundException(f"Tag with this id {tag_id} not found")

        return tag

    async def get_tags(self) -> list[TagDB]:
        return await self.tag_repo.get_all()

    async def delete_tag(self, tag_id: int) -> None:
        await self.tag_repo.delete(tag_id)
