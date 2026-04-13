import re
from app.models.domain import Category, Tag

class CategoryRepository:
    def __init__(self) -> None:
        self._categories: dict[int, Category] = {}
        self._counter: int = 1

    def _sluggify(self, name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    def create(self, name: str) -> Category:
        category = Category(
            id=self._counter,
            name=name,
            slug=self._sluggify(name)
        )

        self._categories[self._counter] = category
        self._counter += 1

        return category

    def get_by_id(self, category_id: int) -> Category | None:
        return self._categories.get(category_id)

    def get_all(self) -> list[Category]:
        return list(self._categories.values())

    def delete(self, category_id: int) -> bool:
        if category_id in self._categories:
            del self._categories[category_id]
            return True

        return False


class TagRepository:
    def __init__(self) -> None:
        self._tags: dict[int, Tag] = {}
        self._counter: int = 1

    def _sluggify(self, name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    def create(self, name: str) -> Tag:
        tag = Tag(
            id=self._counter,
            name=name,
            slug=self._sluggify(name)
        )

        self._tags[self._counter] = tag
        self._counter += 1

        return tag

    def get_by_id(self, tag_id: int) -> Tag | None:
        return self._tags.get(tag_id)

    def get_all(self) -> list[Tag]:
        return list(self._tags.values())

    def delete(self, tag_id: int) -> bool:
        if tag_id in self._tags:
            del self._tags[tag_id]
            return True

        return False
