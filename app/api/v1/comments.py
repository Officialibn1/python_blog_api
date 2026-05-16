from fastapi import APIRouter, Depends, Query, status
from app.core.exceptions import AuthorizationException
from app.schemas.common import PaginatedResponse
from app.services.comments_service import CommentService
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.core.dependencies import get_comment_service, get_post_service, require_admin, get_current_user
from app.services.post_service import PostService

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CommentCreate,
    service: CommentService = Depends(get_comment_service),
    post_service: PostService = Depends(get_post_service),
    current_user: dict = Depends(get_current_user)
):
    await post_service.get_post(post_id=data.post_id)
    return await service.create(data, author_name=current_user["username"])

@router.get("/{post_id}", response_model=PaginatedResponse[CommentResponse])
async def get_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    service: CommentService = Depends(get_comment_service),
    post_service: PostService = Depends(get_post_service)
):
    await post_service.get_post(post_id)
    data, total = await service.get_post_comments(post_id, page, size)
    return PaginatedResponse(
        items=data,
        total=total,
        page=page,
        size=size,
        pages=-(-total // size)
    )

@router.patch("/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
async def edit_comment(
    comment_id: int,
    data: CommentUpdate,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user)
):
    verify = await service.get_comment(comment_id)
    if verify.author_name != current_user["username"]:
        raise AuthorizationException("You do not have permission to edit this comment")

    return await service.edit_comment(comment_id, body=data.body)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.delete_comment(comment_id)
