from fastapi import APIRouter, Depends, Query, status
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.schemas.common import PaginatedResponse
from app.services.post_service import PostService
from app.core.dependencies import get_post_service, get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/", response_model=PaginatedResponse[PostResponse])
async def get_posts(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Total items per page"),
    published_only: bool = Query(False, description="Show only publised posts"),
    service: PostService = Depends(get_post_service)
):
    posts, total = await service.list_posts(page=page, size=size, published_only=published_only)
    return PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        size=size,
        pages=-(-total // size)
    )

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    service: PostService = Depends(get_post_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.create_post(data)

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
):
    return await service.get_post(post_id)

@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int, data: PostUpdate,
    service: PostService = Depends(get_post_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.update_post(post_id, data)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
    current_user: dict = Depends(get_current_user)
):
    await service.delete_post(post_id)
