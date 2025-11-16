from pydantic import BaseModel
from typing import Optional

class Vehicle(BaseModel):
    vehicle_id: Optional[str] = None
    customer_id: str
    registration_number: str
    make: str
    model: str
    year: int
    color: Optional[str] = None
    vin: Optional[str] = None  # Vehicle Identification Number
    mileage: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class VehicleCreate(BaseModel):
    customer_id: str
    registration_number: str
    make: str
    model: str
    year: int
    color: Optional[str] = None
    vin: Optional[str] = None
    mileage: Optional[int] = None

class VehicleUpdate(BaseModel):
    color: Optional[str] = None
    mileage: Optional[int] = None