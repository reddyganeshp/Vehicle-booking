from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate
from app.crud.vehicle_crud import VehicleCRUD
from app.non_crud_lib.storage_service import StorageService
from app.non_crud_lib.validator import Validator

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

vehicle_crud = VehicleCRUD()
storage_service = StorageService()
validator = Validator()

@router.post("/", response_model=Vehicle)
async def create_vehicle(vehicle_data: VehicleCreate):
    """Create a new vehicle"""
    # Validate registration number (NON-CRUD)
    reg_validation = validator.validate_vehicle_registration(vehicle_data.registration_number)
    if not reg_validation['is_valid']:
        raise HTTPException(status_code=400, detail=reg_validation['message'])
    
    # Validate VIN if provided (NON-CRUD)
    if vehicle_data.vin:
        vin_validation = validator.validate_vin(vehicle_data.vin)
        if not vin_validation['is_valid']:
            raise HTTPException(status_code=400, detail=vin_validation['message'])
    
    # Create vehicle (CRUD)
    vehicle = vehicle_crud.create_vehicle(vehicle_data)
    return vehicle

@router.get("/", response_model=List[Vehicle])
async def get_all_vehicles():
    """Get all vehicles"""
    return vehicle_crud.get_all_vehicles()

@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: str):
    """Get vehicle by ID"""
    vehicle = vehicle_crud.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.put("/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(vehicle_id: str, vehicle_data: VehicleUpdate):
    """Update vehicle"""
    vehicle = vehicle_crud.update_vehicle(vehicle_id, vehicle_data)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.delete("/{vehicle_id}")
async def delete_vehicle(vehicle_id: str):
    """Delete vehicle"""
    success = vehicle_crud.delete_vehicle(vehicle_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete vehicle")
    return {"message": "Vehicle deleted successfully"}

@router.post("/{vehicle_id}/upload-image")
async def upload_vehicle_image(vehicle_id: str, file: UploadFile = File(...)):
    """Upload vehicle image (NON-CRUD - S3)"""
    vehicle = vehicle_crud.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    file_content = await file.read()
    result = storage_service.upload_vehicle_image(
        vehicle_id=vehicle_id,
        image_content=file_content,
        image_name=file.filename
    )
    
    if result['status'] == 'error':
        raise HTTPException(status_code=500, detail=result['message'])
    
    return result

@router.get("/{vehicle_id}/validate")
async def validate_vehicle(vehicle_id: str):
    """Validate vehicle details (NON-CRUD)"""
    vehicle = vehicle_crud.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    reg_validation = validator.validate_vehicle_registration(vehicle.registration_number)
    vin_validation = validator.validate_vin(vehicle.vin) if vehicle.vin else {'is_valid': True, 'message': 'No VIN provided'}
    
    return {
        'vehicle_id': vehicle_id,
        'registration_validation': reg_validation,
        'vin_validation': vin_validation
    }

@router.get("/customer/{customer_id}", response_model=List[Vehicle])
async def get_customer_vehicles(customer_id: str):
    """Get all vehicles for a customer"""
    return vehicle_crud.get_vehicles_by_customer(customer_id)