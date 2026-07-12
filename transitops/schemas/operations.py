from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

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

class FuelLogCreate(BaseModel):
    vehicle_id: int
    liters: float
    cost: float
    date: date

class FuelLogOut(FuelLogCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ExpenseCreate(BaseModel):
    vehicle_id: int
    trip_id: Optional[int]
    type: str
    amount: float
    date: date

class ExpenseOut(ExpenseCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
