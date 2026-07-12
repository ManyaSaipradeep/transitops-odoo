from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import auth, vehicles, drivers, maintenance, trips, fuel_expenses, analytics
from database import Base, engine
import models.users
import models.fleet
import models.operations

# Ensure tables are created (optional but good for testing without migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TransitOps")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth.router, tags=["auth"])
app.include_router(vehicles.router, tags=["vehicles"])
app.include_router(drivers.router, tags=["drivers"])
app.include_router(maintenance.router, tags=["maintenance"])
app.include_router(trips.router, tags=["trips"])
app.include_router(fuel_expenses.router, tags=["fuel_expenses"])
app.include_router(analytics.router, tags=["analytics"])

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

from fastapi.responses import RedirectResponse
from fastapi import HTTPException, status, Depends
from auth.dependencies import get_current_user, get_db, oauth2_scheme
from routers.analytics import get_dashboard
from sqlalchemy.orm import Session

@app.get("/dashboard")
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    try:
        credentials = await oauth2_scheme(request)
        current_user = get_current_user(request=request, credentials=credentials, db=db)
    except HTTPException:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    data = get_dashboard(db=db, current_user=current_user)
    
    return templates.TemplateResponse(request=request, name="dashboard.html", context=data)

from routers.analytics import get_fuel_efficiency, get_vehicle_roi

@app.get("/fleet")
async def fleet_page(request: Request, db: Session = Depends(get_db)):
    try:
        credentials = await oauth2_scheme(request)
        current_user = get_current_user(request=request, credentials=credentials, db=db)
    except HTTPException:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    vehicles = db.query(models.fleet.Vehicle).all()
    return templates.TemplateResponse(request=request, name="fleet.html", context={"vehicles": vehicles})

@app.get("/drivers-page")
async def drivers_page(request: Request, db: Session = Depends(get_db)):
    try:
        credentials = await oauth2_scheme(request)
        current_user = get_current_user(request=request, credentials=credentials, db=db)
    except HTTPException:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    drivers = db.query(models.fleet.Driver).all()
    return templates.TemplateResponse(request=request, name="drivers.html", context={"drivers": drivers})

@app.get("/trips-page")
async def trips_page(request: Request, db: Session = Depends(get_db)):
    try:
        credentials = await oauth2_scheme(request)
        current_user = get_current_user(request=request, credentials=credentials, db=db)
    except HTTPException:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    trips = db.query(models.operations.Trip).all()
    return templates.TemplateResponse(request=request, name="trips.html", context={"trips": trips})

@app.get("/maintenance-page")
async def maintenance_page(request: Request, db: Session = Depends(get_db)):
    try:
        credentials = await oauth2_scheme(request)
        current_user = get_current_user(request=request, credentials=credentials, db=db)
    except HTTPException:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    logs = db.query(models.fleet.MaintenanceLog).all()
    return templates.TemplateResponse(request=request, name="maintenance.html", context={"logs": logs})

@app.get("/fuel-expenses-page")
async def fuel_expenses_page(request: Request, db: Session = Depends(get_db)):
    try:
        credentials = await oauth2_scheme(request)
        current_user = get_current_user(request=request, credentials=credentials, db=db)
    except HTTPException:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    fuel_logs = db.query(models.operations.FuelLog).all()
    expenses = db.query(models.operations.Expense).all()
    return templates.TemplateResponse(request=request, name="fuel_expenses.html", context={"fuel_logs": fuel_logs, "expenses": expenses})

@app.get("/analytics-page")
async def analytics_page(request: Request, db: Session = Depends(get_db)):
    try:
        credentials = await oauth2_scheme(request)
        current_user = get_current_user(request=request, credentials=credentials, db=db)
    except HTTPException:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    dashboard_data = get_dashboard(db=db, current_user=current_user)
    fuel_efficiency_data = get_fuel_efficiency(db=db, current_user=current_user)
    vehicle_roi_data = get_vehicle_roi(db=db, current_user=current_user)
    
    return templates.TemplateResponse(request=request, name="analytics.html", context={
        "fleet_utilization_pct": dashboard_data["fleet_utilization_pct"],
        "fuel_efficiency": fuel_efficiency_data,
        "vehicle_roi": vehicle_roi_data
    })

@app.get("/settings-page")
async def settings_page(request: Request, db: Session = Depends(get_db)):
    try:
        credentials = await oauth2_scheme(request)
        current_user = get_current_user(request=request, credentials=credentials, db=db)
    except HTTPException:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
    return templates.TemplateResponse(request=request, name="settings.html", context={"user": current_user})