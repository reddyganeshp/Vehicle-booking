from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import os

app = FastAPI(
    title="Vehicle Service Booking System",
    version="1.0.0",
    description="Vehicle Service Booking System - Mock Version (No AWS Required)"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
customers_db = {}
vehicles_db = {}
bookings_db = {}
service_centers_db = {}

# Models
class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

class Customer(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    created_at: str

class VehicleCreate(BaseModel):
    customer_id: str
    registration_number: str
    make: str
    model: str
    year: int
    color: Optional[str] = None
    vin: Optional[str] = None
    mileage: Optional[int] = None

class Vehicle(BaseModel):
    vehicle_id: str
    customer_id: str
    registration_number: str
    make: str
    model: str
    year: int
    color: Optional[str] = None
    vin: Optional[str] = None
    mileage: Optional[int] = None
    created_at: str

class BookingCreate(BaseModel):
    customer_id: str
    vehicle_id: str
    service_center_id: str
    service_type: str
    booking_date: str
    scheduled_time: str
    notes: Optional[str] = None

class Booking(BaseModel):
    booking_id: str
    customer_id: str
    vehicle_id: str
    service_center_id: str
    service_type: str
    booking_date: str
    scheduled_time: str
    status: str
    estimated_cost: Optional[float] = None
    notes: Optional[str] = None
    created_at: str

class ServiceCenterCreate(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: str
    services_offered: List[str]
    working_hours: Optional[str] = "9:00 AM - 6:00 PM"

class ServiceCenter(BaseModel):
    service_center_id: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: str
    services_offered: List[str]
    working_hours: str
    created_at: str

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Routes
@app.get("/")
async def root():
    html_file = os.path.join(static_path, "index.html")
    if os.path.exists(html_file):
        return FileResponse(html_file)
    
    return {
        "message": "Welcome to Vehicle Service Booking System",
        "version": "1.0.0",
        "status": "active (mock mode - no AWS required)",
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mode": "mock",
        "total_customers": len(customers_db),
        "total_bookings": len(bookings_db),
        "total_vehicles": len(vehicles_db),
        "total_service_centers": len(service_centers_db)
    }

# Customer endpoints
@app.post("/customers/", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    customer_id = str(uuid.uuid4())
    new_customer = Customer(
        customer_id=customer_id,
        **customer.dict(),
        created_at=datetime.utcnow().isoformat()
    )
    customers_db[customer_id] = new_customer.dict()
    return new_customer

@app.get("/customers/", response_model=List[Customer])
async def get_customers():
    return [Customer(**c) for c in customers_db.values()]

@app.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    return Customer(**customers_db[customer_id])

@app.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str):
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    del customers_db[customer_id]
    return {"message": "Customer deleted successfully"}

# Vehicle endpoints
@app.post("/vehicles/", response_model=Vehicle)
async def create_vehicle(vehicle: VehicleCreate):
    # Check if customer exists
    if vehicle.customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    vehicle_id = str(uuid.uuid4())
    new_vehicle = Vehicle(
        vehicle_id=vehicle_id,
        **vehicle.dict(),
        created_at=datetime.utcnow().isoformat()
    )
    vehicles_db[vehicle_id] = new_vehicle.dict()
    return new_vehicle

@app.get("/vehicles/", response_model=List[Vehicle])
async def get_vehicles():
    return [Vehicle(**v) for v in vehicles_db.values()]

@app.get("/vehicles/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: str):
    if vehicle_id not in vehicles_db:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return Vehicle(**vehicles_db[vehicle_id])

@app.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: str):
    if vehicle_id not in vehicles_db:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    del vehicles_db[vehicle_id]
    return {"message": "Vehicle deleted successfully"}

# Booking endpoints
@app.post("/bookings/", response_model=Booking)
async def create_booking(booking: BookingCreate):
    # Validate references
    if booking.customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    if booking.vehicle_id not in vehicles_db:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if booking.service_center_id not in service_centers_db:
        raise HTTPException(status_code=404, detail="Service center not found")
    
    booking_id = str(uuid.uuid4())
    
    # Calculate estimated cost based on service type
    cost_map = {
        "OIL_CHANGE": 50.00,
        "TIRE_ROTATION": 40.00,
        "BRAKE_SERVICE": 150.00,
        "ENGINE_DIAGNOSTIC": 100.00,
        "FULL_SERVICE": 300.00,
        "GENERAL_REPAIR": 80.00
    }
    estimated_cost = cost_map.get(booking.service_type, 100.00)
    
    new_booking = Booking(
        booking_id=booking_id,
        **booking.dict(),
        status="PENDING",
        estimated_cost=estimated_cost,
        created_at=datetime.utcnow().isoformat()
    )
    bookings_db[booking_id] = new_booking.dict()
    return new_booking

@app.get("/bookings/", response_model=List[Booking])
async def get_bookings():
    return [Booking(**b) for b in bookings_db.values()]

@app.get("/bookings/{booking_id}", response_model=Booking)
async def get_booking(booking_id: str):
    if booking_id not in bookings_db:
        raise HTTPException(status_code=404, detail="Booking not found")
    return Booking(**bookings_db[booking_id])

@app.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: str):
    if booking_id not in bookings_db:
        raise HTTPException(status_code=404, detail="Booking not found")
    del bookings_db[booking_id]
    return {"message": "Booking cancelled successfully"}

# Service Center endpoints
@app.post("/service-centers/", response_model=ServiceCenter)
async def create_service_center(service_center: ServiceCenterCreate):
    service_center_id = str(uuid.uuid4())
    new_service_center = ServiceCenter(
        service_center_id=service_center_id,
        **service_center.dict(),
        created_at=datetime.utcnow().isoformat()
    )
    service_centers_db[service_center_id] = new_service_center.dict()
    return new_service_center

@app.get("/service-centers/", response_model=List[ServiceCenter])
async def get_service_centers():
    return [ServiceCenter(**sc) for sc in service_centers_db.values()]

@app.get("/service-centers/{service_center_id}", response_model=ServiceCenter)
async def get_service_center(service_center_id: str):
    if service_center_id not in service_centers_db:
        raise HTTPException(status_code=404, detail="Service center not found")
    return ServiceCenter(**service_centers_db[service_center_id])

@app.delete("/service-centers/{service_center_id}")
async def delete_service_center(service_center_id: str):
    if service_center_id not in service_centers_db:
        raise HTTPException(status_code=404, detail="Service center not found")
    del service_centers_db[service_center_id]
    return {"message": "Service center deleted successfully"}

# Initialize with sample data
@app.on_event("startup")
async def startup_event():
    # Create sample service center
    sc_id = str(uuid.uuid4())
    service_centers_db[sc_id] = {
        "service_center_id": sc_id,
        "name": "Quick Auto Service",
        "address": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "phone": "555-0100",
        "email": "service@quickauto.com",
        "services_offered": ["OIL_CHANGE", "TIRE_ROTATION", "BRAKE_SERVICE", "FULL_SERVICE"],
        "working_hours": "9:00 AM - 6:00 PM",
        "created_at": datetime.utcnow().isoformat()
    }
    print(f"✅ Sample service center created: {sc_id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)