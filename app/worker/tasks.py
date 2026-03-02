import asyncio
from sqlalchemy import select
from app.worker.celery import celery
from app.db.session import SessionLocal
from app.db.models import Job, Run
from app.services.job_runner import run_job
from datetime import datetime, timezone

@celery.task(name="coreops.execute_job")
def execute_job(run_id: int):
    db = SessionLocal()
    try:
        run = db.get(Run, run_id)
        if not run:
            return

        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        db.commit()

        job = db.get(Job, run.job_id)
        if not job:
            run.status = "failed"
            run.error = "Job not found"
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            return

        result = asyncio.run(run_job(job.type, job.payload))

        run.status = "success"
        run.output = result
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        run = db.get(Run, run_id)
        if run:
            run.status = "failed"
            run.error = str(e)
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()