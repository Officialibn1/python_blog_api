from fastapi import HTTPException, status
from app.repositories.category_repository import CategoryRepository, TagRepository
from app.schemas.category import CategoryCreate
from app.schemas.tag import TagCreate
from app.models.domain import Category, Tag

class CategoryService:
    def __init__(self, category_repo: CategoryRepository) -> None:
        self.category_repo = category_repo

    def create_category(self, data: CategoryCreate) -> Category:
        category = self.category_repo.create(
            name=data.name
        )
        return category

    def get_category(self, category_id: int) -> Category:
        category = self.category_repo.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with this id {category_id} not found")

        return category

    def get_all(self) -> list[Category]:
        return self.category_repo.get_all()

    def delete_category(self, category_id: int) -> None:
        success = self.category_repo.delete(category_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with this id {category_id} not found")

class TagService:
    def __init__(self, tag_repo: TagRepository) -> None:
        self.tag_repo = tag_repo

    def create(self, data: TagCreate) -> Tag:
        tag = self.tag_repo.create(
            name=data.name
        )
        return tag

    def get_tag(self, tag_id: int) -> Tag:
        tag = self.tag_repo.get_by_id(tag_id)
        if tag is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag with this id {tag_id} not found")

        return tag

    def get_tags(self) -> list[Tag]:
        return self.tag_repo.get_all()

    def delete_tag(self, tag_id: int) -> None:
        success = self.tag_repo.delete(tag_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag with this id {tag_id} not found")
