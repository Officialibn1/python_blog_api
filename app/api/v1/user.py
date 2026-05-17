from fastapi import APIRouter, Query, Depends, Request
from app.core.dependencies import get_post_service, get_user_service
from app.schemas.post import PostResponse
from app.services.post_service import PostService
from app.services.user_service import UserService
from app.core.dependencies import require_admin, get_current_user
from app.schemas.user import UserResponse, AdminUpdateUser, UserUpdateUser
from app.schemas.common import PaginatedResponse
from app.core.limiter import limiter
from app.core.exceptions import AuthorizationException

router = APIRouter(prefix="/users", tags=["Users"])

rate_limit_message = "Your browser is maing too many requests"

@router.get("/", response_model=PaginatedResponse[UserResponse])
@limiter.limit(limit_value="20/minute", per_method=True, error_message=rate_limit_message)
async def get_user(
    request: Request,
    page: int = Query(1, ge=1, description="Current page number"),
    size: int = Query(10, ge=10, le=100, description="Total number of records per page"),
    current_user: dict = Depends(require_admin),
    service: UserService = Depends(get_user_service)
):
    users, total = await service.get_users(page, size)
    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        size=size,
        pages=-(-total // size)
    )

@router.get("/me", response_model=UserResponse)
@limiter.limit(limit_value="10/minute", per_method=True, error_message=rate_limit_message)
async def get_profile(
    request: Request,
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return await service.get_user(user_id=current_user["id"])

@router.put("/me", response_model=UserResponse)
@limiter.limit(limit_value="10/minute", per_method=True, error_message=rate_limit_message)
async def update_profile(
    data: UserUpdateUser,
    request: Request,
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return await service.update_user(user_id=current_user["id"], data=data)

@router.get("/{user_id}", response_model=UserResponse)
@limiter.limit(limit_value="5/minute", per_method=True, error_message=rate_limit_message)
async def get_user_by_id(request: Request, user_id: int, service: UserService = Depends(get_user_service)):
    return await service.get_user(user_id)

@router.put("/{user_id}", response_model=UserResponse)
@limiter.limit(limit_value="10/minute", per_method=True, error_message=rate_limit_message)
async def update_user(
    user_id: int,
    data: AdminUpdateUser,
    request: Request,
    service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user),
):
    if current_user["id"] != user_id and current_user["role"] != "admin":
        raise AuthorizationException("You can'not edit another user profile")

    return await service.update_user(user_id, data)

@router.patch("/{user_id}", response_model=UserResponse)
@limiter.limit(limit_value='5/minute', per_method=True, error_message="Your browser is making requests at abnormal rates")
async def activate_or_deactivate_user(
    user_id: int,
    request: Request,
    service: UserService = Depends(get_user_service),
    current_user: dict = Depends(require_admin)
):
    return await service.toggle_user_active_status(user_id)

@router.get("/{author_id}/posts", response_model=PaginatedResponse[PostResponse])
async def get_authors_posts(
    author_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Total items per page"),
    published_only: bool = Query(False, description="Show only published posts"),
    service: PostService = Depends(get_post_service),
    current_user: dict = Depends(get_current_user)
):
    posts, total = await service.list_authors_posts(author_id, page, size, current_user, published_only)
    return PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        size=size,
        pages=-(-total // size)
    )
