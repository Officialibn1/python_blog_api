from app.repositories.post_repository import PostRepository
from app.repositories.category_repository import CategoryRepository, TagRepository
from app.schemas.post import PostCreate, PostUpdate
from app.models.db import PostDB
from app.core.exceptions import ConflictException, NotFoundException, AuthorizationException

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

    async def create_post(self, data: PostCreate, current_user: dict) -> PostDB:
        exist = await self.post_repo.verify_slug(data.title)
        if exist:
            raise ConflictException("Blog with this title already exists")

        if not await self.category_repo.get_by_id(data.category_id):
            raise NotFoundException(f"Category with this id {data.category_id} not found")

        tags = []
        for tag_id in data.tag_ids:
            tag = await self.tag_repo.get_by_id(tag_id)
            if not tag:
                raise NotFoundException(f"Tag with this id {tag_id} not found")
            else:
                tags.append(tag)

        post = await self.post_repo.create(
            title=data.title,
            content=data.content,
            category_id=data.category_id,
            published=data.published,
            author_id=current_user["id"]
        )

        post.tags = tags
        await self.post_repo.db.flush()

        return await self.get_post(post.id)

    async def get_post(self, post_id: int) -> PostDB:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with this id {post_id} not found")

        return post

    async def list_posts(self, page: int, size: int, published_only: bool) -> tuple[list[PostDB], int]:
        skip = (page - 1) * size
        result = await self.post_repo.get_all(published_only=published_only, skip=skip, limit=size)

        return result

    async def update_post(self, post_id: int, data: PostUpdate, current_user: dict) -> PostDB:
        post_exist = await self.post_repo.verify_slug(title=data.title)
        if post_exist and post_exist.id != post_id:
            raise ConflictException("A blog with this title already exist")

        post = await self.get_post(post_id)
        if post.author_id is None or post.author_id != current_user["id"]:
            raise AuthorizationException("You do not have permission to modify this post")

        updated_post = await self.post_repo.update(post_id, **data.model_dump(exclude_none=True))

        return updated_post

    async def delete_post(self, post_id: int, current_user: dict) -> None:
        post = await self.get_post(post_id)
        if post.author_id is not None and post.author_id != current_user["id"] and current_user["role"] != "admin":
            raise AuthorizationException("You do not have permission to delete this post")
        await self.post_repo.delete(post_id)
