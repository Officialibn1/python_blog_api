from fastapi import APIRouter, Depends, status
from app.services.comments_service import CommentService
from app.schemas.comment import CommentCreate, CommentResponse
from app.core.dependencies import get_comment_service, get_post_service, get_current_user
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
    return await service.create(data)

@router.get("/{post_id}", response_model=list[CommentResponse])
async def get_comments(
    post_id: int,
    service: CommentService = Depends(get_comment_service),
    post_service: PostService = Depends(get_post_service)
):
    await post_service.get_post(post_id)
    return await service.get_post_comments(post_id)

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    service: CommentService = Depends(get_comment_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.delete_comment(comment_id)
