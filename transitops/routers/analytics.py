from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from auth.dependencies import require_role, get_db, get_current_user
from models.fleet import Vehicle, Driver, MaintenanceLog
from models.operations import Trip, FuelLog
import io
import csv

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    vehicles = db.query(Vehicle).all()
    trips = db.query(Trip).all()
    drivers = db.query(Driver).all()
    
    active_vehicles = sum(1 for v in vehicles if v.status != "Retired")
    available_vehicles = sum(1 for v in vehicles if v.status == "Available")
    vehicles_in_maintenance = sum(1 for v in vehicles if v.status == "In Shop")
    
    active_trips = sum(1 for t in trips if t.status == "Dispatched")
    pending_trips = sum(1 for t in trips if t.status == "Draft")
    
    drivers_on_duty = sum(1 for d in drivers if d.status == "On Trip")
    
    fleet_utilization_pct = 0.0
    if active_vehicles > 0:
        fleet_utilization_pct = round((active_trips / active_vehicles) * 100, 1)
        
    return {
        "active_vehicles": active_vehicles,
        "available_vehicles": available_vehicles,
        "vehicles_in_maintenance": vehicles_in_maintenance,
        "active_trips": active_trips,
        "pending_trips": pending_trips,
        "drivers_on_duty": drivers_on_duty,
        "fleet_utilization_pct": fleet_utilization_pct
    }

@router.get("/fuel-efficiency")
def get_fuel_efficiency(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    vehicles = db.query(Vehicle).all()
    results = []
    
    for v in vehicles:
        completed_trips = db.query(Trip).filter(Trip.vehicle_id == v.id, Trip.status == "Completed").all()
        if not completed_trips:
            continue
            
        total_planned_distance = sum(t.planned_distance for t in completed_trips)
        total_fuel_consumed = sum((t.fuel_consumed or 0.0) for t in completed_trips)
        
        if total_fuel_consumed > 0:
            efficiency = round(total_planned_distance / total_fuel_consumed, 2)
            results.append({
                "vehicle_id": v.id,
                "registration_number": v.registration_number,
                "distance_per_fuel": efficiency
            })
            
    return results

@router.get("/vehicle-roi")
def get_vehicle_roi(
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Financial Analyst", "Fleet Manager"]))
):
    vehicles = db.query(Vehicle).all()
    results = []
    
    for v in vehicles:
        if v.acquisition_cost == 0:
            continue
            
        completed_trips = db.query(Trip).filter(Trip.vehicle_id == v.id, Trip.status == "Completed").all()
        total_revenue = sum(t.revenue for t in completed_trips)
        
        fuel_logs = db.query(FuelLog).filter(FuelLog.vehicle_id == v.id).all()
        total_fuel_cost = sum(log.cost for log in fuel_logs)
        
        maintenance_logs = db.query(MaintenanceLog).filter(MaintenanceLog.vehicle_id == v.id).all()
        total_maintenance_cost = sum(log.cost for log in maintenance_logs)
        
        roi = round((total_revenue - (total_maintenance_cost + total_fuel_cost)) / v.acquisition_cost, 4)
        results.append({
            "vehicle_id": v.id,
            "registration_number": v.registration_number,
            "roi": roi
        })
        
    return results

@router.get("/export-csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["Financial Analyst", "Fleet Manager"]))
):
    vehicles = db.query(Vehicle).all()
    active_vehicles_count = sum(1 for v in vehicles if v.status != "Retired")
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "registration_number", 
        "status", 
        "total_fuel_cost", 
        "total_maintenance_cost", 
        "total_operational_cost", 
        "fleet_utilization contribution", 
        "roi"
    ])
    
    for v in vehicles:
        # Cost
        fuel_logs = db.query(FuelLog).filter(FuelLog.vehicle_id == v.id).all()
        total_fuel_cost = sum(log.cost for log in fuel_logs)
        
        maintenance_logs = db.query(MaintenanceLog).filter(MaintenanceLog.vehicle_id == v.id).all()
        total_maintenance_cost = sum(log.cost for log in maintenance_logs)
        
        total_operational_cost = total_fuel_cost + total_maintenance_cost
        
        # Fleet utilization contribution
        active_trips_for_v = db.query(Trip).filter(Trip.vehicle_id == v.id, Trip.status == "Dispatched").count()
        utilization = 0.0
        if active_vehicles_count > 0 and v.status != "Retired":
             utilization = round((active_trips_for_v / active_vehicles_count) * 100, 2)
             
        # ROI
        roi = ""
        if v.acquisition_cost > 0:
            completed_trips = db.query(Trip).filter(Trip.vehicle_id == v.id, Trip.status == "Completed").all()
            total_revenue = sum(t.revenue for t in completed_trips)
            roi = round((total_revenue - total_operational_cost) / v.acquisition_cost, 4)
            
        writer.writerow([
            v.registration_number,
            v.status,
            total_fuel_cost,
            total_maintenance_cost,
            total_operational_cost,
            utilization,
            roi
        ])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers={"Content-Disposition": 'attachment; filename="transitops_report.csv"'}
    )
