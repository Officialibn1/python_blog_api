from fastapi import HTTPException, status
from app.repositories.post_repository import PostRepository
from app.repositories.category_repository import CategoryRepository, TagRepository
from app.schemas.post import PostCreate, PostUpdate
from app.models.db import PostDB

class PostService:
    def __init__(
        self,
        post_repo: PostRepository,
        category_repo: CategoryRepository,
        tag_repo: TagRepository
    ) -> None:
        self.post_repo = post_repo
        self.category_repo = category_repo
        self.tag_repo = tag_repo

    async def create_post(self, data: PostCreate) -> PostDB:
        if not await self.category_repo.get_by_id(data.category_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with this id {data.category_id} not found")

        tags = []
        for tag_id in data.tag_ids:
            tag = await self.tag_repo.get_by_id(tag_id)
            if not tag:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag with this id {tag_id} not found")
            else:
                tags.append(tag)

        post = await self.post_repo.create(
            title=data.title,
            content=data.content,
            category_id=data.category_id,
            published=data.published
        )

        post.tags = tags
        await self.post_repo.db.flush()
        await self.post_repo.db.refresh(post)

        return post

    async def get_post(self, post_id: int) -> PostDB:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with this id {post_id} not found")


        return post

    async def list_posts(self, page: int, size: int, published_only: bool) -> tuple[list[PostDB], int]:
        skip = (page - 1) * size
        result = await self.post_repo.get_all(published_only=published_only, skip=skip, limit=size, )

        return result

    async def update_post(self, post_id: int, data: PostUpdate) -> PostDB:
        await self.get_post(post_id)

        updated_post = await self.post_repo.update(post_id, **data.model_dump(exclude_none=True))
        if not updated_post:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred while updating post")

        return updated_post

    async def delete_post(self, post_id: int) -> None:
        deleted = await self.post_repo.delete(post_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with this id {post_id} not found")
