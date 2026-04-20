from fastapi import APIRouter, Depends, status
from app.services.categories_service import TagService
from app.schemas.tag import TagCreate, TagResponse
from app.core.dependencies import get_tag_service, require_admin

router = APIRouter(prefix="/tags", tags=["Tags"])

@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    service: TagService = Depends(get_tag_service),
    current_user: dict = Depends(require_admin)
):
    return await service.create(data)

@router.get("/", response_model=list[TagResponse])
async def get_tags(service: TagService = Depends(get_tag_service)):
    return await service.get_tags()

@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: int, service: TagService = Depends(get_tag_service)):
    return await service.get_tag(tag_id)

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    service: TagService = Depends(get_tag_service),
    current_user: dict = Depends(require_admin)
):
    await service.delete_tag(tag_id)
