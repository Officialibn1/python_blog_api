from fastapi import APIRouter, Depends, status
from app.services.comments_service import CommentService
from app.schemas.comment import CommentCreate, CommentResponse
from app.core.dependencies import get_comment_service, get_post_service
from app.services.post_service import PostService

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    data: CommentCreate,
    service: CommentService = Depends(get_comment_service),
    post_service: PostService = Depends(get_post_service)
):
    post_service.get_post(post_id=data.post_id)
    return service.create(data)

@router.get("/{post_id}", response_model=list[CommentResponse])
def get_comments(
    post_id: int,
    service: CommentService = Depends(get_comment_service),
    post_service: PostService = Depends(get_post_service)
):
    post_service.get_post(post_id)
    return service.get_post_comments(post_id)

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, service: CommentService = Depends(get_comment_service)):
    return service.delete_comment(comment_id)
