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