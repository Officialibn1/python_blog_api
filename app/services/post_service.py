from fastapi import HTTPException, status
from app.repositories.post_repository import PostRepository
from app.repositories.category_repository import CategoryRepository, TagRepository
from app.schemas.post import PostCreate, PostUpdate
from app.models.domain import Post

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

    def _enrich(self, post: Post) -> Post:
        post.category = self.category_repo.get_by_id(post.category_id)
        post.tags = [
            tag for tag_id in post.tag_ids
            if (tag:= self.tag_repo.get_by_id(tag_id)) is not None
        ]
        return post

    def create_post(self, data: PostCreate) -> Post:
        if not self.category_repo.get_by_id(data.category_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with this id {data.category_id} not found")

        for tag_id in data.tag_ids:
            if not self.tag_repo.get_by_id(tag_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag with this id {tag_id} not found")

        post = self.post_repo.create(
            title=data.title,
            content=data.content,
            category_id=data.category_id,
            tag_ids=data.tag_ids,
            published=data.published
        )

        return self._enrich(post)

    def get_post(self, post_id: int) -> Post:
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with this id {post_id} not found")

        return self._enrich(post)

    def list_posts(self, page: int, size: int, published_only: bool) -> tuple[list[Post], int]:
        skip = (page - 1) * size
        posts, total = self.post_repo.get_all(skip, limit=size, published_only=published_only)

        return [self._enrich(p) for p in posts], total

    def update_post(self, post_id: int, data: PostUpdate) -> Post:
        self.get_post(post_id)

        updated_post = self.post_repo.update(post_id, **data.model_dump(exclude_none=True))
        if not updated_post:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred while updating post")

        return self._enrich(updated_post)

    def delete_post(self, post_id: int) -> None:
        deleted = self.post_repo.delete(post_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with this id {post_id} not found")
