import json
from app.core.exceptions import NotFoundException
from app.repositories.category_repository import CategoryRepository, TagRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.tag import TagCreate, TagUpdate
from app.models.db import CategoryDB, TagDB
from app.core.cache import cache_get, cache_set, cache_delete

CATEGORIES_CACHE_KEY = "categories:all"
TAGS_CACHE_KEY = "tags:all"

class CategoryService:
    def __init__(self, category_repo: CategoryRepository) -> None:
        self.category_repo = category_repo

    async def create_category(self, data: CategoryCreate) -> CategoryDB:
        category = await self.category_repo.create(
            name=data.name
        )
        await cache_delete(CATEGORIES_CACHE_KEY)
        return category

    async def update_category(self, category_id: int, data: CategoryUpdate) -> CategoryDB:
        category = await self.category_repo.update(category_id, name=data.name)
        await cache_delete(CATEGORIES_CACHE_KEY)
        return category

    async def get_category(self, category_id: int) -> CategoryDB:
        category = await self.category_repo.get_by_id(category_id)
        if category is None:
            raise NotFoundException(f"Category with this id {category_id} not found")

        return category

    async def get_all(self) -> list[CategoryDB]:
        cached = await cache_get(CATEGORIES_CACHE_KEY)
        if cached:
            return json.loads(cached)


        categories =  await self.category_repo.get_all()
        serialized = json.dumps([
            {"id": c.id, "name": c.name, "slug": c.slug, "created_at": c.created_at.isoformat()} for c in categories
        ])
        await cache_set(key=CATEGORIES_CACHE_KEY, value=serialized, ttl=300)
        return categories

    async def delete_category(self, category_id: int) -> None:
        await self.category_repo.delete(category_id)
        await cache_delete(CATEGORIES_CACHE_KEY)

class TagService:
    def __init__(self, tag_repo: TagRepository) -> None:
        self.tag_repo = tag_repo

    async def create(self, data: TagCreate) -> TagDB:
        tag = await self.tag_repo.create(
            name=data.name
        )
        await cache_delete(TAGS_CACHE_KEY)
        return tag

    async def update_tag(self, tag_id: int, data: TagUpdate) -> TagDB:
        tag = await self.tag_repo.update(tag_id, name=data.name)
        await cache_delete(TAGS_CACHE_KEY)
        return tag

    async def get_tag(self, tag_id: int) -> TagDB:
        tag = await self.tag_repo.get_by_id(tag_id)
        if tag is None:
            raise NotFoundException(f"Tag with this id {tag_id} not found")

        return tag

    async def get_tags(self) -> list[TagDB]:
        cache = await cache_get(TAGS_CACHE_KEY)
        if cache:
            return json.loads(cache)

        tags = await self.tag_repo.get_all()
        serialized = json.dumps([
            {"id": t.id, "name": t.name, "slug": t.slug} for t in tags
        ])
        await cache_set(key=TAGS_CACHE_KEY, value=serialized, ttl=300)
        return tags

    async def delete_tag(self, tag_id: int) -> None:
        await self.tag_repo.delete(tag_id)
        await cache_delete(TAGS_CACHE_KEY)
