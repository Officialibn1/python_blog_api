from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_jwt_token
from app.repositories.user_repository import UserRepository
from app.repositories.post_repository import PostRepository
from app.repositories.category_repository import CategoryRepository, TagRepository
from app.repositories.comment_repository import CommentRepository
from app.services.categories_service import CategoryService, TagService
from app.services.comments_service import CommentService
from app.services.post_service import PostService
from app.services.user_service import UserService
from app.core.exceptions import AuthenticationException, AuthorizationException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
bearer_scheme = HTTPBearer()

# Singletons - To maintain one instance for the applications lifecycle
def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_post_repo(db: AsyncSession = Depends(get_db)) -> PostRepository:
    return PostRepository(db)

def get_comment_repo(db: AsyncSession = Depends(get_db)) -> CommentRepository:
    return CommentRepository(db)

def get_category_repo(db: AsyncSession = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db)

def get_tag_repo(db: AsyncSession = Depends(get_db)) -> TagRepository:
    return TagRepository(db)

def get_user_service(user_repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo)

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


# Autorization and Authentication related dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    token = credentials.credentials
    data = decode_jwt_token(token)
    if data.get("token_type") != "access":
        raise AuthenticationException("Invalid token type")

    return data

async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise AuthorizationException("Admin access required")

    return current_user

async def can_create_post(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") not in ["admin", "author"]:
        raise AuthorizationException("Insufficent access to perform this action")

    return current_user
