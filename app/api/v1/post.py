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
    service: PostService = Depends(get_post_service)
):
    posts, total = await service.list_posts(page=page, size=size)
    return PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        size=size,
        pages=-(-total // size)
    )

@router.get("/{author_id}", response_model=PaginatedResponse[PostResponse])
async def get_authors_posts(
    author_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Total items per page"),
    published_only: bool = Query(False, description="Show only published posts"),
    service: PostService = Depends(get_post_service),
    current_user: dict = Depends(get_current_user)
):
    posts, total = await service.list_authors_posts(author_id, page, size, published_only, current_user)
    return PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        size=size,
        pages=-(-total // size)
    )

@router.get("/public_posts/author/{author_id}", response_model=PaginatedResponse[PostResponse])
async def get_public_authors_posts(
    author_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Total items per page"),
    service: PostService = Depends(get_post_service),
):
    posts, total = await service.list_authors_posts(author_id, page, size)
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
    return await service.create_post(data, current_user)

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
    return await service.update_post(post_id, data, current_user)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
    current_user: dict = Depends(get_current_user)
):
    await service.delete_post(post_id, current_user)
