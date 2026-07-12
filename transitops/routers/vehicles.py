from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.dependencies import require_role, get_db
from models.fleet import Vehicle
from schemas.fleet import VehicleCreate, VehicleOut, VehicleUpdate

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.post("/", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle: VehicleCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(require_role(["Fleet Manager"]))
):
    existing = db.query(Vehicle).filter(Vehicle.registration_number == vehicle.registration_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle with this registration number already exists")
    
    new_vehicle = Vehicle(**vehicle.model_dump())
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return new_vehicle

@router.get("/", response_model=list[VehicleOut])
def list_vehicles(
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Fleet Manager", "Driver", "Safety Officer", "Financial Analyst"]))
):
    return db.query(Vehicle).all()

@router.get("/available", response_model=list[VehicleOut])
def list_available_vehicles(
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Fleet Manager", "Driver", "Safety Officer", "Financial Analyst"]))
):
    return db.query(Vehicle).filter(Vehicle.status == "Available").all()

@router.put("/{id}", response_model=VehicleOut)
def update_vehicle(
    id: int, 
    vehicle_update: VehicleUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Fleet Manager"]))
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    update_data = vehicle_update.model_dump(exclude_unset=True)
    if "registration_number" in update_data and update_data["registration_number"] != vehicle.registration_number:
        existing = db.query(Vehicle).filter(Vehicle.registration_number == update_data["registration_number"]).first()
        if existing:
             raise HTTPException(status_code=400, detail="Vehicle with this registration number already exists")

    for key, value in update_data.items():
        setattr(vehicle, key, value)
        
    db.commit()
    db.refresh(vehicle)
    return vehicle

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Fleet Manager"]))
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db.delete(vehicle)
    db.commit()
    return None
