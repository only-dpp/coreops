from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Job, Run
from app.core.security import get_csrf_token, verify_csrf
from app.web.routes.auth import require_login

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


def base_ctx(request: Request):
    return {
        "request": request,
        "csrf_token": get_csrf_token(request),
        "current_user_email": request.session.get("user_email"),
    }


@router.get("/dashboard")
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    auth_redirect = require_login(request)
    if auth_redirect:
        return auth_redirect

    counts, monitors = build_dashboard_data(db)
    ctx = base_ctx(request)
    ctx.update({"counts": counts, "monitors": monitors})

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=ctx,
    )
@router.get("/dashboard/monitors/new")
def monitor_new_page(request: Request):
    auth_redirect = require_login(request)
    if auth_redirect:
        return auth_redirect

    ctx = base_ctx(request)
    ctx = base_ctx(request)
    return templates.TemplateResponse(
        request=request,
        name="monitor_form.html",
        context=ctx,
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
    csrf_token: str = Form(...),
):
    auth_redirect = require_login(request)
    if auth_redirect:
        return auth_redirect

    verify_csrf(request, csrf_token)

    if alert_channel not in {"discord", "email"}:
        raise HTTPException(status_code=400, detail="Canal inválido")

    job = Job(
        owner_id=request.session["user_id"],
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


@router.post("/dashboard/monitors/{job_id}/toggle")
def monitor_toggle(
    request: Request,
    job_id: int,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
):
    auth_redirect = require_login(request)
    if auth_redirect:
        return auth_redirect

    verify_csrf(request, csrf_token)

    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Monitor not found")

    job.enabled = not job.enabled
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/dashboard/monitors/{job_id}/delete")
def monitor_delete(
    request: Request,
    job_id: int,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
):
    auth_redirect = require_login(request)
    if auth_redirect:
        return auth_redirect

    verify_csrf(request, csrf_token)

    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Monitor not found")

    db.delete(job)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/dashboard/partials/summary-cards")
def dashboard_summary_cards(request: Request, db: Session = Depends(get_db)):
    auth_redirect = require_login(request)
    if auth_redirect:
        return auth_redirect

    counts, _ = build_dashboard_data(db)
    ctx = base_ctx(request)
    ctx.update({"counts": counts})
    ctx = base_ctx(request)
    return templates.TemplateResponse(
        request=request,
        name="partials/_summary_card.html",
        context=ctx,
    )



@router.get("/dashboard/partials/monitors-table")
def dashboard_monitors_table(request: Request, db: Session = Depends(get_db)):
    auth_redirect = require_login(request)
    if auth_redirect:
        return auth_redirect

    _, monitors = build_dashboard_data(db)
    ctx = base_ctx(request)
    ctx.update({"monitors": monitors})
    return templates.TemplateResponse(
        request=request,
        name="partials/_summary_table.html",
        context=ctx,
    )


@router.get("/dashboard/monitors/{job_id}")
def monitor_detail_page(request: Request, job_id: int, db: Session = Depends(get_db)):
    auth_redirect = require_login(request)
    if auth_redirect:
        return auth_redirect

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

    ctx = base_ctx(request)
    ctx.update({"monitor": monitor, "runs": runs_data})
    return templates.TemplateResponse(
        request=request,
        name="monitor_detail.html",
        context=ctx,
    )


@router.get("/dashboard/partials/monitor/{job_id}/status")
def monitor_status_partial(request: Request, job_id: int, db: Session = Depends(get_db)):
    auth_redirect = require_login(request)
    if auth_redirect:
        return auth_redirect

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

    ctx = base_ctx(request)
    ctx.update({"monitor": monitor})
    return templates.TemplateResponse(
        request=request,
        name="partials/_monitor_status.html",
        context=ctx,
    )


@router.get("/dashboard/partials/monitor/{job_id}/runs")
def monitor_runs_partial(request: Request, job_id: int, db: Session = Depends(get_db)):
    auth_redirect = require_login(request)
    if auth_redirect:
        return auth_redirect

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

    ctx = base_ctx(request)
    ctx.update({"runs": runs_data})
    return templates.TemplateResponse(
        request=request,
        name="partials/_monitor_runs.html",
        context=ctx,
    )