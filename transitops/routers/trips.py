from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from auth.dependencies import require_role, get_db, get_current_user
from models.operations import Trip
from models.fleet import Vehicle, Driver
from schemas.operations import TripCreate, TripOut, TripComplete

router = APIRouter(prefix="/trips", tags=["trips"])

@router.post("/", response_model=TripOut, status_code=status.HTTP_201_CREATED)
def create_trip(
    trip_in: TripCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Driver", "Fleet Manager"]))
):
    if trip_in.vehicle_id:
        vehicle = db.query(Vehicle).filter(Vehicle.id == trip_in.vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=400, detail="Vehicle not found")
        # Validate cargo_weight <= Vehicle's max_load_capacity
        if trip_in.cargo_weight > vehicle.max_load_capacity:
            raise HTTPException(status_code=400, detail="Cargo weight exceeds vehicle capacity")

    if trip_in.driver_id:
        driver = db.query(Driver).filter(Driver.id == trip_in.driver_id).first()
        if not driver:
            raise HTTPException(status_code=400, detail="Driver not found")

    new_trip = Trip(**trip_in.model_dump())
    new_trip.status = "Draft"
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    return new_trip

@router.put("/{id}/dispatch", response_model=TripOut)
def dispatch_trip(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Driver", "Fleet Manager"]))
):
    trip = db.query(Trip).filter(Trip.id == id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.status != "Draft":
        raise HTTPException(status_code=400, detail="Only Draft trips can be dispatched")

    if not trip.vehicle_id or not trip.driver_id:
        raise HTTPException(status_code=400, detail="Vehicle and driver must be assigned to dispatch")

    vehicle = db.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()
    driver = db.query(Driver).filter(Driver.id == trip.driver_id).first()

    if not vehicle or vehicle.status != "Available":
        raise HTTPException(status_code=400, detail="Vehicle not available")

    today = date.today()
    if not driver or driver.status != "Available" or driver.license_expiry_date < today:
        raise HTTPException(status_code=400, detail="Driver not available or license expired")

    # Atomic transaction
    try:
        trip.status = "Dispatched"
        vehicle.status = "On Trip"
        driver.status = "On Trip"
        db.commit()
        db.refresh(trip)
        return trip
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to dispatch trip atomically")

@router.put("/{id}/complete", response_model=TripOut)
def complete_trip(
    id: int,
    completion_data: TripComplete,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Driver", "Fleet Manager"]))
):
    trip = db.query(Trip).filter(Trip.id == id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.status != "Dispatched":
        raise HTTPException(status_code=400, detail="Trip is not dispatched")

    vehicle = db.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()
    driver = db.query(Driver).filter(Driver.id == trip.driver_id).first()

    # Atomic transaction
    try:
        trip.status = "Completed"
        trip.final_odometer = completion_data.final_odometer
        trip.fuel_consumed = completion_data.fuel_consumed
        
        if vehicle:
            vehicle.odometer = completion_data.final_odometer
            vehicle.status = "Available"
        if driver:
            driver.status = "Available"

        db.commit()
        db.refresh(trip)
        return trip
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to complete trip atomically")

@router.put("/{id}/cancel", response_model=TripOut)
def cancel_trip(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Driver", "Fleet Manager"]))
):
    trip = db.query(Trip).filter(Trip.id == id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.status != "Dispatched":
        raise HTTPException(status_code=400, detail="Only dispatched trips can be cancelled")

    vehicle = db.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()
    driver = db.query(Driver).filter(Driver.id == trip.driver_id).first()

    # Atomic transaction
    try:
        trip.status = "Cancelled"
        
        if vehicle:
            vehicle.status = "Available"
        if driver:
            driver.status = "Available"

        db.commit()
        db.refresh(trip)
        return trip
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to cancel trip atomically")

@router.get("/", response_model=list[TripOut])
def list_trips(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(Trip).all()

@router.get("/{id}", response_model=TripOut)
def get_trip(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    trip = db.query(Trip).filter(Trip.id == id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
