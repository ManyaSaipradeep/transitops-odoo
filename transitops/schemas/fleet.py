from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class VehicleCreate(BaseModel):
    registration_number: str
    name_model: str
    type: str
    max_load_capacity: float
    odometer: float
    acquisition_cost: float
    status: Optional[str] = "Available"

class VehicleUpdate(BaseModel):
    registration_number: Optional[str] = None
    name_model: Optional[str] = None
    type: Optional[str] = None
    max_load_capacity: Optional[float] = None
    odometer: Optional[float] = None
    acquisition_cost: Optional[float] = None
    status: Optional[str] = None

class VehicleOut(VehicleCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DriverCreate(BaseModel):
    name: str
    license_number: str
    license_category: str
    license_expiry_date: date
    contact_number: str
    safety_score: Optional[float] = 100.0
    status: Optional[str] = "Available"

class DriverUpdate(BaseModel):
    name: Optional[str] = None
    license_number: Optional[str] = None
    license_category: Optional[str] = None
    license_expiry_date: Optional[date] = None
    contact_number: Optional[str] = None
    safety_score: Optional[float] = None
    status: Optional[str] = None

class DriverOut(DriverCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class MaintenanceLogCreate(BaseModel):
    vehicle_id: int
    service_type: str
    cost: float
    date: date
    status: Optional[str] = "Active"

class MaintenanceLogOut(MaintenanceLogCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
