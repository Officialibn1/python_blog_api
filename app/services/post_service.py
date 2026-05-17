import json
from app.repositories.post_repository import PostRepository
from app.repositories.category_repository import CategoryRepository, TagRepository
from app.schemas.post import PostCreate, PostUpdate
from app.models.db import PostDB
from app.core.exceptions import ConflictException, NotFoundException, AuthorizationException
from app.core.cache import cache_get, cache_set, cache_delete_pattern

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

    def _serialize_post(self, post: PostDB) -> dict:
        return {
          "id": post.id,
          "title": post.title,
          "slug": post.slug,
          "content": post.content,
          "author_id": post.author_id,
          "category_id": post.category_id,
          "category": {
            "name": post.category.name,
            "id": post.category.id,
            "slug": post.category.slug
          },
          "published": post.published,
          "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in post.tags],
          "created_at": post.created_at.isoformat(),
          "updated_at": post.updated_at.isoformat() if post.updated_at else None
        }

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
        await cache_delete_pattern("post*")

        return await self._get_post_db(post.id)

    async def get_post(self, post_id: int) -> PostDB:
        cached = await cache_get(f"post:{post_id}")
        if cached:
            return json.loads(cached)

        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with this id {post_id} not found")

        await cache_set(
            f"post:{post_id}",
            json.dumps(self._serialize_post(post)),
            ttl=300
        )

        return post

    async def _get_post_db(self, post_id: int) -> PostDB:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException(f"Post with this id {post_id} not found")
        return post

    async def list_posts(
        self,
        page: int,
        size: int,
        author_id: int | None = None,
        search_term: str | None = None,
        category_id: int | None = None,
        tag_id: int | None = None,
        published_only: bool = True
    ) -> tuple[list[PostDB], int]:
        skip = (page - 1) * size
        key = f"posts:page={page}:size={size}:author_id={author_id}:search_term={search_term}:category_id={category_id}:tag_id={tag_id}:published_only={published_only}"
        cached = await cache_get(key)
        if cached:
            data = json.loads(cached)
            return data["data"], data["total"]

        posts, total = await self.post_repo.get_all(
            published_only=published_only,
            skip=skip,
            limit=size,
            author_id=author_id,
            search_term=search_term,
            category_id=category_id,
            tag_id=tag_id
        )

        await cache_set(
            key,
            json.dumps({
                "data": [self._serialize_post(post) for post in posts],
                "total": total
            }),
            ttl=300
        )

        return posts, total

    async def list_authors_posts(
        self,
        author_id: int,
        page: int,
        size: int,
        current_user: dict,
        published_only: bool = True,
    ) -> tuple[list[PostDB], int]:
        # is_owner = current_user["id"] == author_id
        # is_admin = current_user["role"] == "admin"
        # if not (is_admin or is_owner):
        #     published_only = True

        if current_user and current_user["id"] != author_id:
            raise AuthorizationException("You do not have permisison to view this author's post")
        skip = (page - 1) * size
        key = f"posts_author:auhtor_id={author_id}:page={page}:size={size}"
        cached = await cache_get(key)
        if cached:
            data = json.loads(cached)
            return data["data"], data["total"]

        posts, total = await self.post_repo.get_all(published_only, author_id, skip=skip, limit=size)
        await cache_set(
            key,
            json.dumps({
                "data": [self._serialize_post(post) for post in posts],
                "total": total
            }),
            ttl=300
        )

        return posts, total

    async def update_post(self, post_id: int, data: PostUpdate, current_user: dict) -> PostDB:
        post_exist = await self.post_repo.verify_slug(title=data.title)
        if post_exist and post_exist.id != post_id:
            raise ConflictException("A blog with this title already exist")

        post = await self._get_post_db(post_id)
        if post.author_id is None or post.author_id != current_user["id"]:
            raise AuthorizationException("You do not have permission to modify this post")

        updated_post = await self.post_repo.update(post_id, **data.model_dump(exclude_none=True))
        await cache_delete_pattern("post*")

        return updated_post

    async def delete_post(self, post_id: int, current_user: dict) -> None:
        post = await self._get_post_db(post_id)
        if post.author_id is not None and post.author_id != current_user["id"] and current_user["role"] != "admin":
            raise AuthorizationException("You do not have permission to delete this post")
        await self.post_repo.delete(post_id)
        await cache_delete_pattern("post*")
