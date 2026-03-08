from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db
from app.db.models import Job, Run
from app.schemas.jobs import JobCreate, JobUpdate, JobOut, MonitorSummaryOut
from app.schemas.runs import RunOut
from app.services.job_runner import run_job  # <- seu job_runner.py (async)

router = APIRouter(prefix="/jobs", tags=["jobs"])

# por enquanto, owner fixo (depois a gente troca por JWT / auth)
OWNER_ID = 1

@router.get("/summary", response_model=list[MonitorSummaryOut])
def get_monitors_summary(db: Session = Depends(get_db)):
    jobs = (
        db.execute(
            select(Job).order_by(Job.id.desc())
        )
        .scalars()
        .all()
    )

    result = []

    for job in jobs:
        if not job.enabled:
            status = "paused"
        elif job.last_status == "success":
            status = "up"
        elif job.last_status == "failed":
            status = "down"
        else:
            status = "pending"

        result.append(
            MonitorSummaryOut(
                id=job.id,
                name=job.name,
                type=job.type,
                enabled=job.enabled,
                status=status,
                interval_seconds=job.interval_seconds,
                last_checked_at=job.last_checked_at,
                last_error=job.last_error,
                consecutive_failures=job.consecutive_failures,
                next_run_at=job.next_run_at,
            )
        )

    return result

@router.get("/{job_id}/runs", response_model=list[RunOut])
def list_job_runs(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    runs = (
        db.execute(
            select(Run)
            .where(Run.job_id == job_id)
            .order_by(Run.id.desc())
        )
        .scalars()
        .all()
    )

    return runs

@router.get("", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return (
        db.query(Job)
        .filter(Job.owner_id == OWNER_ID)
        .order_by(Job.id.desc())
        .all()
    )


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = Job(
        owner_id=OWNER_ID,
        name=payload.name,
        type=payload.type,
        payload=payload.payload,
        enabled=payload.enabled,
        interval_seconds=payload.interval_seconds,
        next_run_at=None,
        alert_channel=payload.alert_channel,
        alert_target=payload.alert_target,
    )

    db.add(job)
    db.commit()
    db.refresh(job)   # <- isso aqui resolve

    return job


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = (
        db.query(Job)
        .filter(Job.owner_id == OWNER_ID, Job.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}", response_model=JobOut)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db)):
    job = (
        db.query(Job)
        .filter(Job.owner_id == OWNER_ID, Job.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # atualiza só o que veio
    if payload.name is not None:
        job.name = payload.name
    if payload.type is not None:
        job.type = payload.type
    if payload.payload is not None:
        job.payload = payload.payload

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = (
        db.query(Job)
        .filter(Job.owner_id == OWNER_ID, Job.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # se quiser também apagar runs do job, dá pra fazer depois com cascade
    db.delete(job)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{job_id}/run", response_model=RunOut, status_code=status.HTTP_201_CREATED)
async def run_job_now(job_id: int, db: Session = Depends(get_db)):
    job = (
        db.query(Job)
        .filter(Job.owner_id == OWNER_ID, Job.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    run = Run(
        job_id=job.id,
        status="running",
        started_at=datetime.now(timezone.utc),
        finished_at=None,
        output=None,
        error=None,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        result = await run_job(job.type, job.payload)
        run.status = "success"
        run.output = result
    except Exception as e:
        run.status = "failed"
        run.error = str(e)
    finally:
        run.finished_at = datetime.now(timezone.utc)
        db.add(run)
        db.commit()
        db.refresh(run)

    return run

