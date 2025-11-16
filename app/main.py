from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.config import config
from app.api import booking_routes, vehicle_routes, customer_routes, service_center_routes

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Vehicle Service Booking System with AWS Integration"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include routers
app.include_router(booking_routes.router)
app.include_router(vehicle_routes.router)
app.include_router(customer_routes.router)
app.include_router(service_center_routes.router)

@app.get("/")
async def root():
    # Serve the HTML dashboard if it exists
    html_file = os.path.join(static_path, "index.html")
    if os.path.exists(html_file):
        return FileResponse(html_file)
    
    # Otherwise return JSON
    return {
        "message": "Welcome to Vehicle Service Booking System",
        "version": config.APP_VERSION,
        "status": "active",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "customers": "/customers/",
            "bookings": "/bookings/",
            "vehicles": "/vehicles/",
            "service_centers": "/service-centers/"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vehicle-booking-system"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)