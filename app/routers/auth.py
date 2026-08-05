from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import verify_password
from app.database import get_db
from app.models import Role, User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/auth/login/employee")
def login_employee(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    return _do_login(request, db, email, password, Role.employee, "/employee")


@router.post("/auth/login/hr")
def login_hr(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    return _do_login(request, db, email, password, Role.hr, "/hr")


def _do_login(
    request: Request,
    db: Session,
    email: str,
    password: str,
    expected_role: Role,
    redirect_to: str,
):
    user = db.query(User).filter(User.email == email).first()
    if (
        user is None
        or user.role != expected_role
        or not verify_password(password, user.password_hash)
    ):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid email or password."},
            status_code=401,
        )
    request.session["user_id"] = user.id
    return RedirectResponse(url=redirect_to, status_code=303)


@router.post("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
