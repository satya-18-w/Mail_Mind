"""Celery worker for scheduled email processing.

Scans Gmail every 5 minutes and runs the AI pipeline.
"""

import datetime

from celery import Celery
from celery.schedules import crontab

from backend.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ai_mail_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "scan-emails-every-5-minutes": {
            "task": "backend.scheduler.worker.scan_and_process_emails",
            "schedule": 300.0,  # 5 minutes
        },
    },
)


@celery_app.task(name="backend.scheduler.worker.scan_and_process_emails")
def scan_and_process_emails():
    """Fetch new emails from Gmail and run through AI pipeline."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from backend.services.gmail_fetcher import GmailFetcher
    from backend.workflows.email_graph import process_email
    from backend.database import crud

    async def _run():
        engine = create_async_engine(settings.database_url)
        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        try:
            fetcher = GmailFetcher()
            fetcher.authenticate()
            raw_emails = fetcher.fetch_emails(max_results=20)
        except Exception as e:
            print(f"[Scheduler] Gmail fetch failed: {e}")
            return {"status": "error", "message": str(e)}

        processed = 0
        async with session_factory() as session:
            for raw in raw_emails:
                try:
                    enriched = process_email(raw)

                    # Convert deadline string to date object
                    deadline_val = None
                    if enriched.get("deadline"):
                        try:
                            deadline_val = datetime.date.fromisoformat(enriched["deadline"])
                        except (ValueError, TypeError):
                            deadline_val = None

                    # Convert timestamp string to datetime object
                    ts = enriched.get("timestamp", datetime.datetime.now(datetime.timezone.utc))
                    if isinstance(ts, str):
                        try:
                            ts = datetime.datetime.fromisoformat(ts)
                        except ValueError:
                            ts = datetime.datetime.now(datetime.timezone.utc)
                    if hasattr(ts, "tzinfo") and ts.tzinfo is not None:
                        ts = ts.replace(tzinfo=None)

                    email_data = {
                        "gmail_id": enriched["gmail_id"],
                        "sender": enriched["sender"],
                        "subject": enriched["subject"],
                        "body": enriched["body"],
                        "timestamp": ts,
                        "category": enriched.get("category"),
                        "subcategory": enriched.get("subcategory"),
                        "priority": enriched.get("priority"),
                        "deadline": deadline_val,
                        "summary": enriched.get("summary"),
                        "embedding": enriched.get("embedding"),
                    }

                    email = await crud.upsert_email(session, email_data)
                    await crud.create_task_from_email(session, email)
                    processed += 1
                except Exception as e:
                    print(f"[Scheduler] Failed to process email {raw.get('gmail_id')}: {e}")

        await engine.dispose()
        return {"status": "success", "processed": processed}

    return asyncio.run(_run())
