from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.post_repository import PostRepository
from app.repositories.category_repository import CategoryRepository, TagRepository
from app.repositories.comment_repository import CommentRepository
from app.services.categories_service import CategoryService, TagService
from app.services.comments_service import CommentService
from app.services.post_service import PostService

# Singletons - To maintain one instance for the applications lifecycle
def get_post_repo(db: AsyncSession = Depends(get_db)) -> PostRepository:
    return PostRepository(db)

def get_comment_repo(db: AsyncSession = Depends(get_db)) -> CommentRepository:
    return CommentRepository(db)

def get_category_repo(db: AsyncSession = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db)

def get_tag_repo(db: AsyncSession = Depends(get_db)) -> TagRepository:
    return TagRepository(db)

def get_post_service(
    post_repo: PostRepository = Depends(get_post_repo),
    category_repo: CategoryRepository = Depends(get_category_repo),
    tag_repo: TagRepository = Depends(get_tag_repo)
) -> PostService:
    return PostService(
        post_repo=post_repo,
        category_repo=category_repo,
        tag_repo=tag_repo
    )

def get_category_service(category_repo: CategoryRepository = Depends(get_category_repo)) -> CategoryService:
    return CategoryService(category_repo)

def get_tag_service(tag_repo: TagRepository = Depends(get_tag_repo)) -> TagService:
    return TagService(tag_repo)

def get_comment_service(comment_repo: CommentRepository = Depends(get_comment_repo)) -> CommentService:
    return CommentService(comment_repo)
