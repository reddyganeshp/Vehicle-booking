from fastapi import APIRouter, HTTPException
from typing import List
from app.models.service_center import ServiceCenter, ServiceCenterCreate, ServiceCenterUpdate
from app.crud.service_center_crud import ServiceCenterCRUD

router = APIRouter(prefix="/service-centers", tags=["service-centers"])

service_center_crud = ServiceCenterCRUD()

@router.post("/", response_model=ServiceCenter)
async def create_service_center(service_center_data: ServiceCenterCreate):
    """Create a new service center"""
    return service_center_crud.create_service_center(service_center_data)

@router.get("/", response_model=List[ServiceCenter])
async def get_all_service_centers():
    """Get all service centers"""
    return service_center_crud.get_all_service_centers()

@router.get("/{service_center_id}", response_model=ServiceCenter)
async def get_service_center(service_center_id: str):
    """Get service center by ID"""
    service_center = service_center_crud.get_service_center(service_center_id)
    if not service_center:
        raise HTTPException(status_code=404, detail="Service center not found")
    return service_center

@router.put("/{service_center_id}", response_model=ServiceCenter)
async def update_service_center(service_center_id: str, service_center_data: ServiceCenterUpdate):
    """Update service center"""
    service_center = service_center_crud.update_service_center(service_center_id, service_center_data)
    if not service_center:
        raise HTTPException(status_code=404, detail="Service center not found")
    return service_center

@router.delete("/{service_center_id}")
async def delete_service_center(service_center_id: str):
    """Delete service center"""
    success = service_center_crud.delete_service_center(service_center_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete service center")
    return {"message": "Service center deleted successfully"}

@router.get("/city/{city}", response_model=List[ServiceCenter])
async def get_service_centers_by_city(city: str):
    """Get service centers by city"""
    return service_center_crud.get_service_centers_by_city(city)