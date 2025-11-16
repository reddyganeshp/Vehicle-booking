from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ServiceType(str, Enum):
    OIL_CHANGE = "OIL_CHANGE"
    TIRE_ROTATION = "TIRE_ROTATION"
    BRAKE_SERVICE = "BRAKE_SERVICE"
    ENGINE_DIAGNOSTIC = "ENGINE_DIAGNOSTIC"
    FULL_SERVICE = "FULL_SERVICE"
    GENERAL_REPAIR = "GENERAL_REPAIR"

class Booking(BaseModel):
    booking_id: Optional[str] = None
    customer_id: str
    vehicle_id: str
    service_center_id: str
    service_type: ServiceType
    booking_date: str
    scheduled_time: str
    status: BookingStatus = BookingStatus.PENDING
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class BookingCreate(BaseModel):
    customer_id: str
    vehicle_id: str
    service_center_id: str
    service_type: ServiceType
    booking_date: str
    scheduled_time: str
    notes: Optional[str] = None

class BookingUpdate(BaseModel):
    service_type: Optional[ServiceType] = None
    booking_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    status: Optional[BookingStatus] = None
    actual_cost: Optional[float] = None
    notes: Optional[str] = None