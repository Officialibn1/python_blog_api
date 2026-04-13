from functools import lru_cache
from app.repositories.post_repository import PostRepository
from app.repositories.category_repository import CategoryRepository, TagRepository
from app.repositories.comment_repository import CommentRepository
from app.services.categories_service import CategoryService, TagService
from app.services.comments_service import CommentService
from app.services.post_service import PostService

# Singletons - To maintain one instance for the applications lifecycle
@lru_cache
def get_post_repo() -> PostRepository:
    return PostRepository()

@lru_cache
def get_comment_repo() -> CommentRepository:
    return CommentRepository()

@lru_cache
def get_category_repo() -> CategoryRepository:
    return CategoryRepository()

@lru_cache
def get_tag_repo() -> TagRepository:
    return TagRepository()

def get_post_service() -> PostService:
    return PostService(
        post_repo=get_post_repo(),
        category_repo=get_category_repo(),
        tag_repo=get_tag_repo()
    )

def get_category_service() -> CategoryService:
    return CategoryService(category_repo=get_category_repo())

def get_tag_service() -> TagService:
    return TagService(tag_repo=get_tag_repo())

def get_comment_service() -> CommentService:
    return CommentService(comment_repo=get_comment_repo())
