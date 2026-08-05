from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.auth import get_current_user
from app.config import SESSION_SECRET
from app.database import get_db
from app.models import Role
from app.routers import auth, employee, hr

app = FastAPI(title="HR Assistant")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(employee.router)
app.include_router(hr.router)


@app.get("/")
def root(request: Request, db=Depends(get_db)):
    user = get_current_user(request, db)
    if user is None:
        return RedirectResponse(url="/login")
    if user.role == Role.hr:
        return RedirectResponse(url="/hr")
    return RedirectResponse(url="/employee")
