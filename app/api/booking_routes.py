from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.models.booking import Booking, BookingCreate, BookingUpdate
from app.crud.booking_crud import BookingCRUD
from app.non_crud_lib.notification_service import NotificationService
from app.non_crud_lib.storage_service import StorageService
from app.non_crud_lib.queue_service import QueueService
from app.non_crud_lib.cost_calculator import CostCalculator
from app.non_crud_lib.validator import Validator
from app.non_crud_lib.scheduler_service import SchedulerService

router = APIRouter(prefix="/bookings", tags=["bookings"])

booking_crud = BookingCRUD()
notification_service = NotificationService()
storage_service = StorageService()
queue_service = QueueService()
cost_calculator = CostCalculator()
validator = Validator()
scheduler_service = SchedulerService()

@router.post("/", response_model=Booking)
async def create_booking(booking_data: BookingCreate):
    """Create a new booking"""
    # Validate booking date
    validation = validator.validate_booking_date(booking_data.booking_date, booking_data.scheduled_time)
    if not validation['is_valid']:
        raise HTTPException(status_code=400, detail=validation['message'])
    
    # Calculate estimated cost
    cost_estimate = cost_calculator.calculate_service_cost(
        service_type=booking_data.service_type,
        estimated_hours=1.5
    )
    
    # Create booking in database (CRUD)
    booking = booking_crud.create_booking(booking_data)
    
    # Update booking with estimated cost
    booking_crud.update_booking(
        booking.booking_id,
        BookingUpdate(estimated_cost=cost_estimate['estimated_total'])
    )
    
    # Queue booking request for processing (NON-CRUD - SQS)
    queue_service.enqueue_booking_request({
        'booking_id': booking.booking_id,
        'customer_id': booking.customer_id,
        'service_type': booking.service_type.value
    })
    
    # Send confirmation notification (NON-CRUD - SNS)
    notification_service.send_booking_confirmation(
        customer_email="customer@example.com",  # Should be fetched from customer data
        booking_details=booking.dict()
    )
    
    # Schedule reminder (NON-CRUD - EventBridge)
    scheduler_service.schedule_booking_reminder(
        booking_id=booking.booking_id,
        booking_datetime=f"{booking.booking_date}T{booking.scheduled_time}",
        customer_email="customer@example.com"
    )
    
    return booking

@router.get("/", response_model=List[Booking])
async def get_all_bookings():
    """Get all bookings"""
    return booking_crud.get_all_bookings()

@router.get("/{booking_id}", response_model=Booking)
async def get_booking(booking_id: str):
    """Get booking by ID"""
    booking = booking_crud.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.put("/{booking_id}", response_model=Booking)
async def update_booking(booking_id: str, booking_data: BookingUpdate):
    """Update booking"""
    booking = booking_crud.update_booking(booking_id, booking_data)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.delete("/{booking_id}")
async def delete_booking(booking_id: str):
    """Delete/Cancel booking"""
    booking = booking_crud.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Send cancellation notification (NON-CRUD - SNS)
    notification_service.send_cancellation_notification(
        customer_email="customer@example.com",
        booking_details=booking.dict()
    )
    
    # Cancel scheduled reminder (NON-CRUD - EventBridge)
    scheduler_service.cancel_scheduled_event(f"vehicle-service-reminders-{booking_id}")
    
    success = booking_crud.delete_booking(booking_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete booking")
    
    return {"message": "Booking cancelled successfully"}

@router.post("/{booking_id}/upload-report")
async def upload_service_report(booking_id: str, file: UploadFile = File(...)):
    """Upload service report (NON-CRUD - S3)"""
    booking = booking_crud.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    file_content = await file.read()
    result = storage_service.upload_service_report(
        booking_id=booking_id,
        file_content=file_content,
        file_name=file.filename
    )
    
    if result['status'] == 'error':
        raise HTTPException(status_code=500, detail=result['message'])
    
    return result

@router.get("/{booking_id}/calculate-cost")
async def calculate_booking_cost(booking_id: str, estimated_hours: float = 1.5):
    """Calculate service cost (NON-CRUD - Pure Logic)"""
    booking = booking_crud.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return cost_calculator.calculate_service_cost(
        service_type=booking.service_type,
        estimated_hours=estimated_hours
    )

@router.get("/customer/{customer_id}", response_model=List[Booking])
async def get_customer_bookings(customer_id: str):
    """Get all bookings for a customer"""
    return booking_crud.get_bookings_by_customer(customer_id)