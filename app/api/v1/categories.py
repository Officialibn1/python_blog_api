from fastapi import APIRouter, status, Depends
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.categories_service import CategoryService
from app.core.dependencies import get_category_service

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, service: CategoryService = Depends(get_category_service)):
   return await service.create_category(data)

@router.get("/", response_model=list[CategoryResponse])
async def get_categories(service: CategoryService = Depends(get_category_service)):
    return await service.get_all()

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, service: CategoryService = Depends(get_category_service)):
    return await service.get_category(category_id)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, service: CategoryService = Depends(get_category_service)):
    await service.delete_category(category_id)
