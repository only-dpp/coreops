from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import User
from app.core.security import verify_password, get_csrf_token, verify_csrf, secrets

from fastapi import Request
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

def require_login(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=303)
    return None

@router.get("/login")
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "csrf_token": get_csrf_token(request),
            "error": None,
        },
    )


@router.post("/login")
def login_submit(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
):
    verify_csrf(request, csrf_token)

    locked_until = request.session.get("login_locked_until")
    if locked_until:
        lock_dt = datetime.fromisoformat(locked_until)
        if lock_dt > datetime.now(timezone.utc):
            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={
                    "request": request,
                    "csrf_token": get_csrf_token(request),
                    "error": "Muitas tentativas. Aguarde alguns minutos.",
                },
                status_code=429,
            )

    user = db.execute(
        select(User).where(User.email == email.strip().lower())
    ).scalar_one_or_none()

    valid = bool(user and verify_password(password, user.password_hash))

    if not valid:
        fail_count = int(request.session.get("login_fail_count", 0)) + 1
        request.session["login_fail_count"] = fail_count

        if fail_count >= 5:
            request.session["login_locked_until"] = (
                datetime.now(timezone.utc) + timedelta(minutes=10)
            ).isoformat()

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "csrf_token": get_csrf_token(request),
                "error": "Credenciais inválidas.",
            },
            status_code=401,
        )

    request.session.clear()
    request.session["user_id"] = user.id
    request.session["user_email"] = user.email
    request.session["csrf_token"] = secrets.token_urlsafe(32)

    return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/logout")
def logout(request: Request, csrf_token: str = Form(...)):
    verify_csrf(request, csrf_token)
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
