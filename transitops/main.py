from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import auth
from database import Base, engine

# Ensure tables are created (optional but good for testing without migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TransitOps")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth.router, tags=["auth"])

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
