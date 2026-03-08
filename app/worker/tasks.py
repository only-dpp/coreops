import asyncio
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app.worker.celery import celery
from app.db.session import SessionLocal
from app.db.models import Job, Run
from app.services.job_runner import run_job
from app.core.config import settings
from app.services.discord_notifier import send_discord_webhook
from app.services.email_notifier import send_email_alert

BRAZIL_TZ = ZoneInfo("America/Sao_Paulo")


def format_dt(dt: datetime | None) -> str:
    if not dt:
        return "N/A"
    return dt.astimezone(BRAZIL_TZ).strftime("%d/%m/%Y %H:%M:%S BRT")


def format_duration(start: datetime | None, end: datetime | None) -> str:
    if not start or not end:
        return "N/A"

    total_seconds = int((end - start).total_seconds())
    if total_seconds < 0:
        total_seconds = 0

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")

    return " ".join(parts)


def build_down_embed(job: Job, error: str, now: datetime) -> dict:
    url = job.payload.get("url", "N/A")
    return {
        "title": "Monitor unavailable",
        "color": 15158332,
        "fields": [
            {"name": "Monitor", "value": job.name, "inline": False},
            {"name": "URL", "value": url, "inline": False},
            {"name": "Status", "value": "Down", "inline": True},
            {"name": "Detected at", "value": format_dt(now), "inline": True},
            {"name": "Error", "value": error[:1000] if error else "N/A", "inline": False},
        ],
    }


def build_recovery_embed(job: Job, result: dict, now: datetime, down_since: datetime | None) -> dict:
    url = job.payload.get("url", "N/A")
    status_code = result.get("status_code", "N/A") if result else "N/A"
    downtime = format_duration(down_since, now)

    return {
        "title": "Monitor recovered",
        "color": 3066993,
        "fields": [
            {"name": "Monitor", "value": job.name, "inline": False},
            {"name": "URL", "value": url, "inline": False},
            {"name": "Status", "value": "Operational", "inline": True},
            {"name": "Status code", "value": str(status_code), "inline": True},
            {"name": "Recovered at", "value": format_dt(now), "inline": True},
            {"name": "Downtime", "value": downtime, "inline": True},
        ],
    }


def build_down_email(job: Job, error: str, now: datetime) -> tuple[str, str, str]:
    url = job.payload.get("url", "N/A")
    subject = f"[CoreOps] Monitor unavailable - {job.name}"

    text_body = (
        f"Monitor: {job.name}\n"
        f"URL: {url}\n"
        f"Status: Down\n"
        f"Detected at: {format_dt(now)}\n"
        f"Error: {error}\n"
    )

    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background:#f3f6fb;font-family:Arial,sans-serif;color:#111827;">
        <div style="max-width:640px;margin:32px auto;background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;overflow:hidden;">
          <div style="padding:20px 24px;background:#0f172a;color:#ffffff;">
            <h2 style="margin:0;font-size:22px;">CoreOps</h2>
            <p style="margin:8px 0 0;color:#cbd5e1;">Monitor unavailable</p>
          </div>

          <div style="padding:24px;">
            <div style="display:inline-block;padding:8px 12px;background:#fee2e2;color:#b91c1c;border-radius:999px;font-weight:700;font-size:13px;">
              DOWN
            </div>

            <table style="width:100%;margin-top:20px;border-collapse:collapse;">
              <tr>
                <td style="padding:10px 0;color:#6b7280;width:150px;">Monitor</td>
                <td style="padding:10px 0;font-weight:600;">{job.name}</td>
              </tr>
              <tr>
                <td style="padding:10px 0;color:#6b7280;">URL</td>
                <td style="padding:10px 0;">
                  <a href="{url}" style="color:#2563eb;text-decoration:none;">{url}</a>
                </td>
              </tr>
              <tr>
                <td style="padding:10px 0;color:#6b7280;">Detected at</td>
                <td style="padding:10px 0;">{format_dt(now)}</td>
              </tr>
            </table>

            <div style="margin-top:20px;padding:16px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:12px;">
              <div style="font-size:12px;color:#6b7280;margin-bottom:8px;text-transform:uppercase;letter-spacing:.04em;">Error</div>
              <div style="font-size:14px;line-height:1.6;color:#111827;">{error}</div>
            </div>
          </div>
        </div>
      </body>
    </html>
    """
    return subject, text_body, html_body


def build_recovery_email(job: Job, result: dict, now: datetime, down_since: datetime | None) -> tuple[str, str, str]:
    url = job.payload.get("url", "N/A")
    status_code = result.get("status_code", "N/A") if result else "N/A"
    downtime = format_duration(down_since, now)

    subject = f"[CoreOps] Monitor recovered - {job.name}"

    text_body = (
        f"Monitor: {job.name}\n"
        f"URL: {url}\n"
        f"Status: Operational\n"
        f"Status code: {status_code}\n"
        f"Recovered at: {format_dt(now)}\n"
        f"Downtime: {downtime}\n"
    )

    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background:#f3f6fb;font-family:Arial,sans-serif;color:#111827;">
        <div style="max-width:640px;margin:32px auto;background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;overflow:hidden;">
          <div style="padding:20px 24px;background:#0f172a;color:#ffffff;">
            <h2 style="margin:0;font-size:22px;">CoreOps</h2>
            <p style="margin:8px 0 0;color:#cbd5e1;">Monitor recovered</p>
          </div>

          <div style="padding:24px;">
            <div style="display:inline-block;padding:8px 12px;background:#dcfce7;color:#166534;border-radius:999px;font-weight:700;font-size:13px;">
              OPERATIONAL
            </div>

            <table style="width:100%;margin-top:20px;border-collapse:collapse;">
              <tr>
                <td style="padding:10px 0;color:#6b7280;width:150px;">Monitor</td>
                <td style="padding:10px 0;font-weight:600;">{job.name}</td>
              </tr>
              <tr>
                <td style="padding:10px 0;color:#6b7280;">URL</td>
                <td style="padding:10px 0;">
                  <a href="{url}" style="color:#2563eb;text-decoration:none;">{url}</a>
                </td>
              </tr>
              <tr>
                <td style="padding:10px 0;color:#6b7280;">Status code</td>
                <td style="padding:10px 0;">{status_code}</td>
              </tr>
              <tr>
                <td style="padding:10px 0;color:#6b7280;">Recovered at</td>
                <td style="padding:10px 0;">{format_dt(now)}</td>
              </tr>
              <tr>
                <td style="padding:10px 0;color:#6b7280;">Downtime</td>
                <td style="padding:10px 0;">{downtime}</td>
              </tr>
            </table>
          </div>
        </div>
      </body>
    </html>
    """
    return subject, text_body, html_body


def send_down_alert(job: Job, error: str, now: datetime) -> None:
    if not job.alert_channel or not job.alert_target:
        return

    if job.alert_channel == "discord":
        send_discord_webhook(
            job.alert_target,
            username=settings.DISCORD_BOT_NAME,
            embeds=[build_down_embed(job, error, now)],
        )
    elif job.alert_channel == "email":
        subject, text_body, html_body = build_down_email(job, error, now)
        send_email_alert(job.alert_target, subject, text_body, html_body)


def send_recovery_alert(job: Job, result: dict, now: datetime, down_since: datetime | None) -> None:
    if not job.alert_channel or not job.alert_target:
        return

    if job.alert_channel == "discord":
        send_discord_webhook(
            job.alert_target,
            username=settings.DISCORD_BOT_NAME,
            embeds=[build_recovery_embed(job, result, now, down_since)],
        )
    elif job.alert_channel == "email":
        subject, text_body, html_body = build_recovery_email(job, result, now, down_since)
        send_email_alert(job.alert_target, subject, text_body, html_body)


@celery.task(name="coreops.execute_job")
def execute_job(run_id: int):
    db = SessionLocal()
    try:
        run = db.get(Run, run_id)
        if not run:
            return

        job = db.get(Job, run.job_id)
        if not job:
            run.status = "failed"
            run.error = "Job not found"
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            return

        previous_last_checked_at = job.last_checked_at
        previous_failures = job.consecutive_failures
        previous_status = job.last_status

        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        db.commit()

        try:
            result = asyncio.run(run_job(job.type, job.payload))
            now = datetime.now(timezone.utc)

            run.status = "success"
            run.output = result
            run.error = None
            run.finished_at = now

            job.last_status = "success"
            job.last_checked_at = now
            job.last_error = None
            job.last_output = result
            job.consecutive_failures = 0

            if previous_status == "failed" and previous_failures >= settings.ALERT_ON_FAILURES:
                send_recovery_alert(job, result, now, previous_last_checked_at)

            db.commit()

        except Exception as e:
            now = datetime.now(timezone.utc)
            error_message = str(e)

            run.status = "failed"
            run.output = None
            run.error = error_message
            run.finished_at = now

            job.last_status = "failed"
            job.last_checked_at = now
            job.last_error = error_message
            job.last_output = None
            job.consecutive_failures += 1

            if job.consecutive_failures == settings.ALERT_ON_FAILURES:
                send_down_alert(job, error_message, now)

            db.commit()

    finally:
        db.close()


@celery.task(name="coreops.tick")
def tick():
    db = SessionLocal()
    now = datetime.now(timezone.utc)

    try:
        jobs = db.execute(
            select(Job).where(Job.enabled == True)
        ).scalars().all()

        for job in jobs:
            if job.next_run_at is None:
                job.next_run_at = now + timedelta(seconds=job.interval_seconds)
                continue

            if job.next_run_at <= now:
                run = Run(job_id=job.id, status="queued")
                db.add(run)
                db.flush()

                execute_job.delay(run.id)
                job.next_run_at = now + timedelta(seconds=job.interval_seconds)

        db.commit()
    finally:
        db.close()