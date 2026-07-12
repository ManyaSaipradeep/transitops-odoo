from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.dependencies import require_role, get_db, get_current_user
from models.operations import FuelLog, Expense
from models.fleet import Vehicle, MaintenanceLog
from schemas.operations import FuelLogCreate, FuelLogOut, ExpenseCreate, ExpenseOut

router = APIRouter(tags=["fuel_expenses"])

@router.post("/fuel-logs", response_model=FuelLogOut, status_code=status.HTTP_201_CREATED)
def create_fuel_log(
    log: FuelLogCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Driver", "Fleet Manager", "Financial Analyst"]))
):
    new_log = FuelLog(**log.model_dump())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@router.get("/fuel-logs", response_model=list[FuelLogOut])
def list_fuel_logs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(FuelLog).all()

@router.post("/expenses", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Driver", "Fleet Manager", "Financial Analyst"]))
):
    new_expense = Expense(**expense.model_dump())
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@router.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(Expense).all()

@router.get("/vehicles/{id}/operational-cost")
def get_vehicle_operational_cost(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Financial Analyst", "Fleet Manager"]))
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
        
    fuel_logs = db.query(FuelLog).filter(FuelLog.vehicle_id == id).all()
    total_fuel_cost = sum(log.cost for log in fuel_logs)
    
    maintenance_logs = db.query(MaintenanceLog).filter(MaintenanceLog.vehicle_id == id).all()
    total_maintenance_cost = sum(log.cost for log in maintenance_logs)
    
    return {
        "vehicle_id": id,
        "total_fuel_cost": total_fuel_cost,
        "total_maintenance_cost": total_maintenance_cost,
        "total_operational_cost": total_fuel_cost + total_maintenance_cost
    }
