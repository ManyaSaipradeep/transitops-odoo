from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import auth, vehicles, drivers, maintenance
from database import Base, engine
import models.users
import models.fleet

# Ensure tables are created (optional but good for testing without migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TransitOps")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth.router, tags=["auth"])
app.include_router(vehicles.router, tags=["vehicles"])
app.include_router(drivers.router, tags=["drivers"])
app.include_router(maintenance.router, tags=["maintenance"])

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")