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