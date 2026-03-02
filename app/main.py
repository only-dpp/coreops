<<<<<<< HEAD
from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.run import router as runs_router

app = FastAPI(title="CoreOps", version="0.1.0")

app.include_router(health_router)
app.include_router(jobs_router)
=======
from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.run import router as runs_router

app = FastAPI(title="CoreOps", version="0.1.0")

app.include_router(health_router)
app.include_router(jobs_router)
>>>>>>> 21599b0b39eba37876fc43d9838497fbe2974000
app.include_router(runs_router)