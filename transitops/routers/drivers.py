from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from models.fleet import Driver
from schemas.fleet import DriverCreate, DriverOut, DriverUpdate
from auth.dependencies import require_role, get_db, get_current_user

router = APIRouter(prefix="/drivers", tags=["drivers"])

@router.post("/", response_model=DriverOut, status_code=status.HTTP_201_CREATED)
def create_driver(
    driver: DriverCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(require_role(["Fleet Manager", "Safety Officer"]))
):
    existing = db.query(Driver).filter(Driver.license_number == driver.license_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Driver with this license number already exists")
    
    new_driver = Driver(**driver.model_dump())
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return new_driver

@router.get("/", response_model=list[DriverOut])
def list_drivers(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(Driver).all()

@router.get("/available", response_model=list[DriverOut])
def list_available_drivers(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    today = date.today()
    return db.query(Driver).filter(
        Driver.status == "Available",
        Driver.license_expiry_date >= today
    ).all()

@router.put("/{id}", response_model=DriverOut)
def update_driver(
    id: int, 
    driver_update: DriverUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Fleet Manager", "Safety Officer"]))
):
    driver = db.query(Driver).filter(Driver.id == id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    update_data = driver_update.model_dump(exclude_unset=True)
    if "license_number" in update_data and update_data["license_number"] != driver.license_number:
        existing = db.query(Driver).filter(Driver.license_number == update_data["license_number"]).first()
        if existing:
             raise HTTPException(status_code=400, detail="Driver with this license number already exists")

    for key, value in update_data.items():
        setattr(driver, key, value)
        
    db.commit()
    db.refresh(driver)
    return driver

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Fleet Manager", "Safety Officer"]))
):
    driver = db.query(Driver).filter(Driver.id == id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    db.delete(driver)
    db.commit()
    return None
