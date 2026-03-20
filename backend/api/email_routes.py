"""FastAPI email routes - /api/v1 endpoints."""

import asyncio
import datetime
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.database import crud
from backend.database.models import User
from backend.api.schemas import (
    EmailOut,
    CategoryOut,
    TaskOut,
    SearchRequest,
    SearchResult,
    PipelineStatus,
    PipelineTriggerRequest,
    PipelineRunOut,
    StatsOverview,
)
from backend.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["emails"])
logger = logging.getLogger(__name__)

# Number of emails to enrich in parallel (LLM calls run concurrently in threads).
PIPELINE_AI_CONCURRENCY = 4


# --- Email Endpoints ---


@router.get("/emails", response_model=list[EmailOut])
async def list_emails(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get all emails ordered by timestamp."""
    return await crud.get_all_emails(db, limit=limit, offset=offset, user_id=user.id)


@router.get("/emails/starred", response_model=list[EmailOut])
async def list_starred_emails(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get starred emails."""
    return await crud.get_starred_emails(db, limit=limit, offset=offset, user_id=user.id)


@router.get("/emails/{email_id}", response_model=EmailOut)
async def get_email(email_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Get a single email by ID."""
    email = await crud.get_email_by_id(db, email_id)
    if not email or getattr(email, "user_id", None) != user.id:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.patch("/emails/{email_id}/read", response_model=EmailOut)
async def mark_as_read(email_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Mark an email as read."""
    email = await crud.mark_email_as_read(db, email_id)
    if not email or getattr(email, "user_id", None) != user.id:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.patch("/emails/{email_id}/star", response_model=EmailOut)
async def toggle_star(email_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Toggle the starred state of an email."""
    email = await crud.toggle_star_email(db, email_id)
    if not email or getattr(email, "user_id", None) != user.id:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.get("/emails/category/{category}", response_model=list[EmailOut])
async def get_emails_by_category(
    category: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get emails filtered by category."""
    valid_categories = {"Institute", "Professor", "LinkedIn", "Society", "Promotion", "Personal"}
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {valid_categories}")
    return await crud.get_emails_by_category(db, category, limit=limit, offset=offset, user_id=user.id)


@router.get("/emails/priority/{priority}", response_model=list[EmailOut])
async def get_emails_by_priority(
    priority: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get emails filtered by priority."""
    valid_priorities = {"HIGH", "MEDIUM", "LOW"}
    if priority.upper() not in valid_priorities:
        raise HTTPException(status_code=400, detail="Invalid priority. Must be HIGH, MEDIUM, or LOW")
    return await crud.get_emails_by_priority(db, priority.upper(), limit=limit, offset=offset, user_id=user.id)


@router.get("/emails/deadlines/upcoming", response_model=list[EmailOut])
async def get_deadlines(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get emails with upcoming deadlines."""
    return await crud.get_emails_with_deadlines(db, limit=limit, user_id=user.id)


# --- Search ---


@router.post("/emails/search", response_model=SearchResult)
async def search_emails(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Semantic search across emails."""
    from backend.services.embedding_service import EmbeddingService

    embedding_service = EmbeddingService()
    query_embedding = embedding_service.embed(request.query)
    emails = await crud.search_emails_by_vector(
        db, query_embedding, limit=request.limit, user_id=user.id
    )
    return SearchResult(emails=emails)


# --- Stats ---


@router.get("/stats/overview", response_model=StatsOverview)
async def get_overview_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get aggregate dashboard statistics."""
    return await crud.get_stats_overview(db, user_id=user.id)


@router.get("/stats/categories")
async def get_category_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get email counts per category."""
    return await crud.get_category_counts(db, user_id=user.id)


@router.get("/stats/priorities")
async def get_priority_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get email counts per priority level."""
    return await crud.get_priority_counts(db, user_id=user.id)


# --- Tasks ---


@router.get("/tasks", response_model=list[TaskOut])
async def get_tasks(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Get all pending tasks."""
    return await crud.get_pending_tasks(db, user_id=user.id)


# --- Pipeline Trigger ---


def _run_pipeline(db_url: str, run_id: int,
                  user_id: int | None = None,
                  access_token: str | None = None,
                  refresh_token: str | None = None,
                  max_results: int = 50):
    """Background task to fetch and process emails."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as AS
    from sqlalchemy.ext.asyncio import async_sessionmaker
    from backend.services.gmail_fetcher import GmailFetcher
    from backend.workflows.email_graph import process_email

    async def _process():
        engine = create_async_engine(db_url)
        session_factory = async_sessionmaker(engine, class_=AS, expire_on_commit=False)

        counters = {"fetched": 0, "processed": 0, "skipped": 0, "failed": 0}

        async with session_factory() as session:
            await crud.update_pipeline_run(
                session, run_id,
                status="RUNNING",
                started_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
            )

        fetcher = GmailFetcher(access_token=access_token, refresh_token=refresh_token)
        try:
            fetcher.authenticate()
            raw_emails = fetcher.fetch_emails(max_results=max_results, days=30)
            counters["fetched"] = len(raw_emails)

            async with session_factory() as session:
                raw_ids = [r.get("gmail_id") for r in raw_emails if r.get("gmail_id")]
                existing_ids = await crud.get_existing_gmail_ids(session, raw_ids, user_id=user_id)

                await crud.update_pipeline_run(session, run_id, fetched_count=counters["fetched"])

                # Partition: skip already-stored, queue new emails for AI enrichment
                to_enrich: list[dict] = []
                for raw in raw_emails:
                    gid = raw.get("gmail_id")
                    if not gid:
                        counters["failed"] += 1
                    elif gid in existing_ids:
                        counters["skipped"] += 1
                    else:
                        to_enrich.append(raw)

                if counters["skipped"] or counters["failed"]:
                    await crud.update_pipeline_run(
                        session, run_id, status="RUNNING",
                        fetched_count=counters["fetched"],
                        skipped_count=counters["skipped"],
                        failed_count=counters["failed"],
                    )

                # ── Parallel AI enrichment: process PIPELINE_AI_CONCURRENCY emails at a time.
                # Each batch runs LLM calls concurrently in threads, then writes to DB and
                # commits so the SSE stream can push live progress to the frontend.
                for batch_start in range(0, len(to_enrich), PIPELINE_AI_CONCURRENCY):
                    batch = to_enrich[batch_start:batch_start + PIPELINE_AI_CONCURRENCY]

                    results = await asyncio.gather(
                        *[asyncio.to_thread(process_email, raw) for raw in batch],
                        return_exceptions=True,
                    )

                    for raw, enriched in zip(batch, results):
                        if isinstance(enriched, BaseException):
                            counters["failed"] += 1
                            logger.exception(
                                "AI enrichment failed gmail_id=%s run_id=%s",
                                raw.get("gmail_id"), run_id, exc_info=enriched,
                            )
                            continue
                        try:
                            gmail_id = enriched["gmail_id"]
                            deadline_val = None
                            if enriched.get("deadline"):
                                try:
                                    deadline_val = datetime.date.fromisoformat(enriched["deadline"])
                                except (ValueError, TypeError):
                                    deadline_val = None

                            ts = enriched.get("timestamp", datetime.datetime.now(datetime.timezone.utc))
                            if isinstance(ts, str):
                                try:
                                    ts = datetime.datetime.fromisoformat(ts)
                                except ValueError:
                                    ts = datetime.datetime.now(datetime.timezone.utc)
                            if hasattr(ts, "tzinfo") and ts.tzinfo is not None:
                                ts = ts.replace(tzinfo=None)

                            email_data = {
                                "gmail_id": gmail_id,
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
                                "user_id": user_id,
                            }

                            email = await crud.upsert_email(session, email_data, autocommit=False)
                            await crud.create_task_from_email(session, email, autocommit=False)
                            existing_ids.add(gmail_id)
                            counters["processed"] += 1
                        except Exception:
                            counters["failed"] += 1
                            logger.exception("DB write failed for run_id=%s", run_id)

                    # Commit this batch and push progress so the SSE stream picks it up
                    await session.commit()
                    await crud.update_pipeline_run(
                        session, run_id, status="RUNNING",
                        fetched_count=counters["fetched"],
                        processed_count=counters["processed"],
                        skipped_count=counters["skipped"],
                        failed_count=counters["failed"],
                    )

                # Final cleanup and completion mark
                await crud.delete_old_emails(session, days=30)
                await crud.update_pipeline_run(
                    session, run_id,
                    status="COMPLETED",
                    fetched_count=counters["fetched"],
                    processed_count=counters["processed"],
                    skipped_count=counters["skipped"],
                    failed_count=counters["failed"],
                    finished_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
                    error_message=None,
                )
        except Exception as exc:
            logger.exception("Pipeline run failed run_id=%s", run_id)
            async with session_factory() as session:
                await crud.update_pipeline_run(
                    session, run_id,
                    status="FAILED",
                    fetched_count=counters["fetched"],
                    processed_count=counters["processed"],
                    skipped_count=counters["skipped"],
                    failed_count=counters["failed"] + 1,
                    finished_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
                    error_message=str(exc)[:2000],
                )
        finally:
            await engine.dispose()

    asyncio.run(_process())


@router.post("/pipeline/run", response_model=PipelineStatus)
async def trigger_pipeline(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    request: PipelineTriggerRequest | None = None,
):
    """Trigger the email processing pipeline."""
    from backend.core.config import get_settings

    if not user.gmail_access_token:
        raise HTTPException(status_code=400, detail="Missing Gmail access token. Please reconnect Google account.")

    settings = get_settings()
    run = await crud.create_pipeline_run(db, user_id=user.id)
    fetch_limit = request.limit if request else 50

    background_tasks.add_task(
        _run_pipeline,
        settings.database_url,
        run.id,
        user.id,
        user.gmail_access_token,
        user.gmail_refresh_token,
        fetch_limit,
    )
    return PipelineStatus(
        status="started",
        run_id=run.id,
        message=f"Pipeline triggered in background for up to {fetch_limit} emails",
    )


@router.get("/pipeline/runs/latest", response_model=PipelineRunOut)
async def get_latest_pipeline_run(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = await crud.get_latest_pipeline_run(db, user_id=user.id)
    if not run:
        raise HTTPException(status_code=404, detail="No pipeline runs found")
    return run


@router.get("/pipeline/runs/stream")
async def stream_latest_pipeline_run(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    async def event_generator():
        last_payload: str | None = None

        while True:
            if await request.is_disconnected():
                break

            run = await crud.get_latest_pipeline_run(db, user_id=user.id)
            if run is None:
                await asyncio.sleep(2)
                continue

            payload = PipelineRunOut.model_validate(run).model_dump(mode="json")
            payload_str = json.dumps(payload)
            if payload_str != last_payload:
                yield f"event: pipeline\ndata: {payload_str}\n\n"
                last_payload = payload_str

            if payload["status"] in {"RUNNING", "QUEUED"}:
                await asyncio.sleep(1)
            else:
                # Keep connection alive while idle and wait for next run changes.
                yield ": keep-alive\n\n"
                await asyncio.sleep(10)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/pipeline/runs/{run_id}", response_model=PipelineRunOut)
async def get_pipeline_run(
    run_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    run = await crud.get_pipeline_run_by_id(db, run_id)
    if not run or run.user_id != user.id:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return run


@router.delete("/emails/cleanup")
async def cleanup_old_emails(days: int = 30, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Delete emails older than the specified number of days."""
    deleted = await crud.delete_old_emails(db, days=days, user_id=user.id)
    return {"deleted": deleted, "message": f"Removed {deleted} emails older than {days} days"}
