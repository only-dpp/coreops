from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import select

from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.run import router as runs_router
from app.web.routes.dashboard import router as dashboard_router
from app.web.routes.auth import router as auth_router
from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.db.models import User

app = FastAPI(title="CoreOps", version="0.1.0")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    session_cookie="coreops_session",
    max_age=settings.SESSION_MAX_AGE_SECONDS,
    same_site="lax",
    https_only=settings.SESSION_HTTPS_ONLY,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
def ensure_admin_user():
    db = SessionLocal()
    try:
        admin_email = settings.ADMIN_EMAIL.strip().lower()
        user = db.execute(select(User).where(User.email == admin_email)).scalar_one_or_none()
        if not user:
            user = User(
                email=admin_email,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
            )
            db.add(user)
            db.commit()
    finally:
        db.close()


app.include_router(auth_router)
app.include_router(health_router)
app.include_router(jobs_router)
app.include_router(runs_router)
app.include_router(dashboard_router)