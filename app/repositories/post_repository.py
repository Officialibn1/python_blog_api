import re
from app.models.domain import Post
from datetime import datetime, timezone

class PostRepository:
    def __init__(self) -> None:
        self._posts: dict[int, Post] = {}
        self._counter: int = 1

    def _slugify(self, title: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

    def create(
        self,
        title: str,
        content: str,
        category_id: int,
        tag_ids: list[int],
        published: bool = False
    ) -> Post:
        post = Post(
            id=self._counter,
            title=title,
            slug=self._slugify(title),
            content=content,
            category_id=category_id,
            tag_ids=tag_ids,
            published=published
        )

        self._posts[self._counter] = post
        self._counter += 1

        return post

    def get_by_id(self, post_id: int) -> Post | None:
        return self._posts.get(post_id)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        published_only: bool = False
    ) -> tuple[list[Post], int]:
        posts = list(self._posts.values())

        if published_only:
            posts = [post for post in posts if post.published]

        total = len(posts)
        return posts[skip: skip + limit], total

    def update(self, post_id: int, **fields) -> Post | None:
        post = self._posts.get(post_id)
        if not post:
            return None

        for key, value in fields.items():
            setattr(post, key, value)

        post.updated_at = datetime.now(timezone.utc)
        return post

    def delete(self, post_id: int) -> bool:
        if post_id in self._posts:
            del self._posts[post_id]
            return True

        return False
