from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.run import router as runs_router
from app.web.routes.dashboard import router as dashboard_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="CoreOps", version="0.1.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(health_router)
app.include_router(jobs_router)
app.include_router(runs_router)
app.include_router(dashboard_router)

