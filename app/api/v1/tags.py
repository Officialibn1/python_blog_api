from fastapi import APIRouter, Depends, status
from app.services.categories_service import TagService
from app.schemas.tag import TagCreate, TagResponse
from app.core.dependencies import get_tag_service

router = APIRouter(prefix="/tags", tags=["Tags"])

@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def crreate_tag(data: TagCreate, service: TagService = Depends(get_tag_service)):
    return service.create(data)

@router.get("/", response_model=list[TagResponse])
def get_tags(service: TagService = Depends(get_tag_service)):
    return service.get_tags()

@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, service: TagService = Depends(get_tag_service)):
    return service.get_tag(tag_id)

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, service: TagService = Depends(get_tag_service)):
    service.delete_tag(tag_id)
