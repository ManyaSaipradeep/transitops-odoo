from pydantic import BaseModel, ConfigDict
from typing import Optional

class TripCreate(BaseModel):
    source: str
    destination: str
    vehicle_id: Optional[int]
    driver_id: Optional[int]
    cargo_weight: float
    planned_distance: float
    revenue: Optional[float] = 0.0

class TripComplete(BaseModel):
    final_odometer: float
    fuel_consumed: float

class TripOut(BaseModel):
    id: int
    source: str
    destination: str
    vehicle_id: Optional[int]
    driver_id: Optional[int]
    cargo_weight: float
    planned_distance: float
    revenue: float
    final_odometer: Optional[float]
    fuel_consumed: Optional[float]
    status: str
    model_config = ConfigDict(from_attributes=True)
