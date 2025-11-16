from fastapi import APIRouter, HTTPException
from typing import List
from app.models.customer import Customer, CustomerCreate, CustomerUpdate
from app.crud.customer_crud import CustomerCRUD
from app.non_crud_lib.validator import Validator
from app.non_crud_lib.report_generator import ReportGenerator
from app.crud.booking_crud import BookingCRUD

router = APIRouter(prefix="/customers", tags=["customers"])

customer_crud = CustomerCRUD()
validator = Validator()
report_generator = ReportGenerator()
booking_crud = BookingCRUD()

@router.post("/", response_model=Customer)
async def create_customer(customer_data: CustomerCreate):
    """Create a new customer"""
    # Validate phone number (NON-CRUD)
    phone_validation = validator.validate_phone_number(customer_data.phone)
    if not phone_validation['is_valid']:
        raise HTTPException(status_code=400, detail=phone_validation['message'])
    
    # Create customer (CRUD)
    customer = customer_crud.create_customer(customer_data)
    return customer

@router.get("/", response_model=List[Customer])
async def get_all_customers():
    """Get all customers"""
    return customer_crud.get_all_customers()

@router.get("/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    """Get customer by ID"""
    customer = customer_crud.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer_data: CustomerUpdate):
    """Update customer"""
    customer = customer_crud.update_customer(customer_id, customer_data)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.delete("/{customer_id}")
async def delete_customer(customer_id: str):
    """Delete customer"""
    success = customer_crud.delete_customer(customer_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete customer")
    return {"message": "Customer deleted successfully"}

@router.get("/{customer_id}/service-history")
async def get_customer_service_history(customer_id: str):
    """Get customer service history report (NON-CRUD)"""
    customer = customer_crud.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get customer bookings
    bookings = booking_crud.get_bookings_by_customer(customer_id)
    bookings_dict = [booking.dict() for booking in bookings]
    
    # Generate report (NON-CRUD)
    report = report_generator.generate_customer_service_history(bookings_dict)
    
    return report