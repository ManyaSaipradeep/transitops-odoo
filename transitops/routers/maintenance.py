from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.dependencies import require_role, get_db, get_current_user
from models.fleet import MaintenanceLog, Vehicle
from schemas.fleet import MaintenanceLogCreate, MaintenanceLogOut

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

@router.post("/", response_model=MaintenanceLogOut, status_code=status.HTTP_201_CREATED)
def create_maintenance(
    log: MaintenanceLogCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Fleet Manager"]))
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == log.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    new_log = MaintenanceLog(**log.model_dump())
    new_log.status = "Active"
    
    # CRITICAL BUSINESS RULE: set linked Vehicle's status to "In Shop"
    vehicle.status = "In Shop"
    
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@router.put("/{id}/close", response_model=MaintenanceLogOut)
def close_maintenance(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Fleet Manager"]))
):
    log = db.query(MaintenanceLog).filter(MaintenanceLog.id == id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    
    log.status = "Closed"
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == log.vehicle_id).first()
    if vehicle:
        # CRITICAL BUSINESS RULE: set linked Vehicle's status back to "Available" UNLESS "Retired"
        if vehicle.status != "Retired":
            vehicle.status = "Available"
            
    db.commit()
    db.refresh(log)
    return log

@router.get("/", response_model=list[MaintenanceLogOut])
def list_maintenance(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(MaintenanceLog).all()
