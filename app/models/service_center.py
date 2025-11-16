from pydantic import BaseModel, EmailStr
from typing import Optional, List

class ServiceCenter(BaseModel):
    service_center_id: Optional[str] = None
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: EmailStr
    services_offered: List[str]
    working_hours: Optional[str] = "9:00 AM - 6:00 PM"
    rating: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ServiceCenterCreate(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: EmailStr
    services_offered: List[str]
    working_hours: Optional[str] = "9:00 AM - 6:00 PM"

class ServiceCenterUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    services_offered: Optional[List[str]] = None
    working_hours: Optional[str] = None
    rating: Optional[float] = None