from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Job, Run

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")

BRAZIL_TZ = ZoneInfo("America/Sao_Paulo")


def fmt_dt(dt: datetime | None) -> str:
    if not dt:
        return "—"
    return dt.astimezone(BRAZIL_TZ).strftime("%d/%m/%Y %H:%M:%S")


def get_monitor_status(job: Job) -> str:
    if not job.enabled:
        return "paused"
    if job.last_status == "success":
        return "up"
    if job.last_status == "failed":
        return "down"
    return "pending"


def build_dashboard_data(db: Session):
    jobs = db.execute(
        select(Job).order_by(Job.id.desc())
    ).scalars().all()

    monitors = []
    counts = {
        "total": 0,
        "up": 0,
        "down": 0,
        "paused": 0,
        "pending": 0,
    }

    for job in jobs:
        status = get_monitor_status(job)
        counts["total"] += 1
        counts[status] += 1

        monitors.append({
            "id": job.id,
            "name": job.name,
            "type": job.type,
            "url": job.payload.get("url", "—"),
            "status": status,
            "enabled": job.enabled,
            "interval_seconds": job.interval_seconds,
            "last_checked_at": fmt_dt(job.last_checked_at),
            "next_run_at": fmt_dt(job.next_run_at),
            "last_error": job.last_error or "—",
            "consecutive_failures": job.consecutive_failures,
            "alert_channel": job.alert_channel,
            "alert_target": job.alert_target or "—",
        })

    return counts, monitors


def build_monitor_detail_data(job: Job, runs: list[Run]):
    monitor = {
        "id": job.id,
        "name": job.name,
        "type": job.type,
        "url": job.payload.get("url", "—"),
        "status": get_monitor_status(job),
        "interval_seconds": job.interval_seconds,
        "enabled": job.enabled,
        "last_checked_at": fmt_dt(job.last_checked_at),
        "next_run_at": fmt_dt(job.next_run_at),
        "last_error": job.last_error or "—",
        "consecutive_failures": job.consecutive_failures,
        "alert_channel": job.alert_channel,
        "alert_target": job.alert_target or "—",
    }

    runs_data = []
    for run in runs:
        runs_data.append({
            "id": run.id,
            "status": run.status,
            "started_at": fmt_dt(run.started_at),
            "finished_at": fmt_dt(run.finished_at),
            "error": run.error or "—",
            "output": run.output,
        })

    return monitor, runs_data


@router.get("/dashboard")
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    counts, monitors = build_dashboard_data(db)
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "counts": counts,
            "monitors": monitors,
        },
    )


@router.get("/dashboard/monitors/new")
def monitor_new_page(request: Request):
    return templates.TemplateResponse(
        "monitor_form.html",
        {
            "request": request,
        },
    )


@router.post("/dashboard/monitors/new")
def monitor_create_from_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    url: str = Form(...),
    expected_status: int = Form(200),
    interval_seconds: int = Form(60),
    alert_channel: str = Form(...),
    alert_target: str = Form(...),
    enabled: bool = Form(False),
):
    job = Job(
        owner_id=1,
        name=name,
        type="http_check",
        payload={
            "url": url,
            "expected_status": expected_status,
        },
        enabled=enabled,
        interval_seconds=interval_seconds,
        next_run_at=None,
        alert_channel=alert_channel,
        alert_target=alert_target,
    )

    db.add(job)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/dashboard/partials/summary-cards")
def dashboard_summary_cards(request: Request, db: Session = Depends(get_db)):
    counts, _ = build_dashboard_data(db)
    return templates.TemplateResponse(
        "partials/_summary_cards.html",
        {
            "request": request,
            "counts": counts,
        },
    )


@router.get("/dashboard/partials/monitors-table")
def dashboard_monitors_table(request: Request, db: Session = Depends(get_db)):
    _, monitors = build_dashboard_data(db)
    return templates.TemplateResponse(
        "partials/_monitors_table.html",
        {
            "request": request,
            "monitors": monitors,
        },
    )


@router.get("/dashboard/monitors/{job_id}")
def monitor_detail_page(request: Request, job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Monitor not found")

    runs = db.execute(
        select(Run)
        .where(Run.job_id == job_id)
        .order_by(Run.id.desc())
        .limit(50)
    ).scalars().all()

    monitor, runs_data = build_monitor_detail_data(job, runs)

    return templates.TemplateResponse(
        "monitor_detail.html",
        {
            "request": request,
            "monitor": monitor,
            "runs": runs_data,
        },
    )


@router.get("/dashboard/partials/monitor/{job_id}/status")
def monitor_status_partial(request: Request, job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Monitor not found")

    runs = db.execute(
        select(Run)
        .where(Run.job_id == job_id)
        .order_by(Run.id.desc())
        .limit(50)
    ).scalars().all()

    monitor, _ = build_monitor_detail_data(job, runs)

    return templates.TemplateResponse(
        "partials/_monitor_status.html",
        {
            "request": request,
            "monitor": monitor,
        },
    )


@router.get("/dashboard/partials/monitor/{job_id}/runs")
def monitor_runs_partial(request: Request, job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Monitor not found")

    runs = db.execute(
        select(Run)
        .where(Run.job_id == job_id)
        .order_by(Run.id.desc())
        .limit(50)
    ).scalars().all()

    _, runs_data = build_monitor_detail_data(job, runs)

    return templates.TemplateResponse(
        "partials/_monitor_runs.html",
        {
            "request": request,
            "runs": runs_data,
        },
    )