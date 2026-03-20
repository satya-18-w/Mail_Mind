"""Database CRUD operations for the email service."""

import datetime
import numpy as np
from sqlalchemy import select, func, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import (
    Email,
    Category,
    Task,
    User,
    PriorityLevel,
    TaskStatus,
    PipelineRun,
)


# ─── User Operations ─────────────────────────────────────────


async def upsert_user(db: AsyncSession, user_data: dict) -> User:
    """Create or update a user by google_id."""
    result = await db.execute(
        select(User).where(User.google_id == user_data["google_id"])
    )
    user = result.scalar_one_or_none()
    if user:
        for key, value in user_data.items():
            if key != "google_id" and value is not None:
                setattr(user, key, value)
    else:
        user = User(**user_data)
        db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user_tokens(
    db: AsyncSession,
    user_id: int,
    access_token: str,
    refresh_token: str | None = None,
    expiry: str | None = None,
) -> User | None:
    """Update a user's Gmail tokens."""
    user = await get_user_by_id(db, user_id)
    if user:
        user.gmail_access_token = access_token
        if refresh_token:
            user.gmail_refresh_token = refresh_token
        if expiry:
            user.gmail_token_expiry = expiry
        await db.commit()
        await db.refresh(user)
    return user


# ─── Email Operations ────────────────────────────────────────


async def upsert_email(
    db: AsyncSession,
    email_data: dict,
    *,
    autocommit: bool = True,
) -> Email:
    """Insert or update an email record.

    Set autocommit=False to batch multiple writes in one transaction.
    """
    lookup = select(Email).where(Email.gmail_id == email_data["gmail_id"])
    if email_data.get("user_id") is not None:
        lookup = lookup.where(Email.user_id == email_data["user_id"])

    result = await db.execute(lookup)
    existing = result.scalar_one_or_none()

    if existing:
        for key, value in email_data.items():
            if key != "gmail_id" and value is not None:
                setattr(existing, key, value)
        email = existing
    else:
        email = Email(**email_data)
        db.add(email)

    try:
        if autocommit:
            await db.commit()
        else:
            await db.flush()
    except IntegrityError:
        # Another concurrent worker inserted the same Gmail message first.
        await db.rollback()
        result = await db.execute(lookup)
        existing = result.scalar_one_or_none()
        if existing is None:
            raise
        for key, value in email_data.items():
            if key != "gmail_id" and value is not None:
                setattr(existing, key, value)
        email = existing
        if autocommit:
            await db.commit()
        else:
            await db.flush()

    if autocommit:
        await db.refresh(email)
    return email


async def email_exists(db: AsyncSession, gmail_id: str, user_id: int | None = None) -> bool:
    """Check if an email already exists (for skip-if-processed optimization)."""
    query = select(func.count()).select_from(Email).where(Email.gmail_id == gmail_id)
    if user_id is not None:
        query = query.where(Email.user_id == user_id)
    result = await db.execute(query)
    return result.scalar() > 0


async def get_existing_gmail_ids(
    db: AsyncSession,
    gmail_ids: list[str],
    user_id: int | None = None,
) -> set[str]:
    """Fetch already persisted Gmail IDs with a single query."""
    if not gmail_ids:
        return set()

    query = select(Email.gmail_id).where(Email.gmail_id.in_(gmail_ids))
    if user_id is not None:
        query = query.where(Email.user_id == user_id)

    result = await db.execute(query)
    return set(result.scalars().all())


async def get_emails_by_category(
    db: AsyncSession, category: str, limit: int = 50, offset: int = 0,
    user_id: int | None = None,
) -> list[Email]:
    """Get emails filtered by category."""
    query = select(Email).where(Email.category == category)
    if user_id is not None:
        query = query.where(Email.user_id == user_id)
    result = await db.execute(
        query.order_by(Email.timestamp.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def get_emails_by_priority(
    db: AsyncSession, priority: str, limit: int = 50, offset: int = 0,
    user_id: int | None = None,
) -> list[Email]:
    """Get emails filtered by priority."""
    query = select(Email).where(Email.priority == priority)
    if user_id is not None:
        query = query.where(Email.user_id == user_id)
    result = await db.execute(
        query.order_by(Email.timestamp.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def get_emails_with_deadlines(
    db: AsyncSession, limit: int = 50, user_id: int | None = None,
) -> list[Email]:
    """Get emails that have deadlines, ordered by deadline."""
    query = select(Email).where(Email.deadline.isnot(None))
    if user_id is not None:
        query = query.where(Email.user_id == user_id)
    result = await db.execute(query.order_by(Email.deadline.asc()).limit(limit))
    return list(result.scalars().all())


async def get_all_emails(
    db: AsyncSession, limit: int = 50, offset: int = 0,
    user_id: int | None = None,
) -> list[Email]:
    """Get all emails ordered by timestamp."""
    query = select(Email)
    if user_id is not None:
        query = query.where(Email.user_id == user_id)
    result = await db.execute(
        query.order_by(Email.timestamp.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def get_email_by_id(db: AsyncSession, email_id: int) -> Email | None:
    """Get a single email by ID."""
    result = await db.execute(select(Email).where(Email.id == email_id))
    return result.scalar_one_or_none()


async def search_emails_by_vector(
    db: AsyncSession, query_embedding: list[float], limit: int = 10,
    user_id: int | None = None,
) -> list[Email]:
    """Semantic search using cosine similarity computed in Python."""
    query = select(Email).where(Email.embedding.isnot(None))
    if user_id is not None:
        query = query.where(Email.user_id == user_id)
    result = await db.execute(query)
    emails = list(result.scalars().all())

    query_vec = np.array(query_embedding)
    scored = []
    for email in emails:
        emb_vec = np.array(email.embedding)
        similarity = np.dot(query_vec, emb_vec) / (
            np.linalg.norm(query_vec) * np.linalg.norm(emb_vec) + 1e-10
        )
        scored.append((similarity, email))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [email for _, email in scored[:limit]]


async def get_category_counts(
    db: AsyncSession, user_id: int | None = None,
) -> list[dict]:
    """Get email count per category."""
    query = (
        select(Email.category, func.count(Email.id).label("count"))
        .where(Email.category.isnot(None))
    )
    if user_id is not None:
        query = query.where(Email.user_id == user_id)
    result = await db.execute(query.group_by(Email.category))
    return [{"name": row.category, "count": row.count} for row in result.all()]


async def get_priority_counts(
    db: AsyncSession, user_id: int | None = None,
) -> list[dict]:
    """Get email count per priority level."""
    query = (
        select(Email.priority, func.count(Email.id).label("count"))
        .where(Email.priority.isnot(None))
    )
    if user_id is not None:
        query = query.where(Email.user_id == user_id)
    result = await db.execute(query.group_by(Email.priority))
    return [{"name": row.priority, "count": row.count} for row in result.all()]


async def get_stats_overview(
    db: AsyncSession, user_id: int | None = None,
) -> dict:
    """Get aggregate stats for the dashboard."""
    base = select(func.count(Email.id)).select_from(Email)
    if user_id is not None:
        base = base.where(Email.user_id == user_id)

    total = (await db.execute(base)).scalar() or 0
    unread = (await db.execute(base.where(Email.is_read == False))).scalar() or 0
    high_pri = (await db.execute(base.where(Email.priority == "HIGH"))).scalar() or 0
    deadlines = (await db.execute(base.where(Email.deadline.isnot(None)))).scalar() or 0
    starred = (await db.execute(base.where(Email.is_starred == True))).scalar() or 0

    return {
        "total": total,
        "unread": unread,
        "high_priority": high_pri,
        "deadlines": deadlines,
        "starred": starred,
    }


async def create_task_from_email(
    db: AsyncSession,
    email: Email,
    *,
    autocommit: bool = True,
) -> Task | None:
    """Create a task if email has a deadline.

    Set autocommit=False to batch task writes in one transaction.
    """
    if not email.deadline:
        return None

    task = Task(
        email_id=email.id,
        deadline=email.deadline,
        status=TaskStatus.PENDING,
        priority=email.priority,
    )
    db.add(task)
    if autocommit:
        await db.commit()
        await db.refresh(task)
    else:
        await db.flush()
    return task


async def get_pending_tasks(db: AsyncSession, user_id: int | None = None) -> list[Task]:
    """Get all pending tasks ordered by deadline."""
    query = (
        select(Task)
        .where(Task.status == TaskStatus.PENDING)
    )
    if user_id is not None:
        query = query.join(Email, Task.email_id == Email.id).where(Email.user_id == user_id)
    result = await db.execute(query.order_by(Task.deadline.asc()))
    return list(result.scalars().all())


async def mark_email_as_read(db: AsyncSession, email_id: int) -> Email | None:
    """Mark an email as read."""
    result = await db.execute(select(Email).where(Email.id == email_id))
    email = result.scalar_one_or_none()
    if email:
        email.is_read = True
        await db.commit()
        await db.refresh(email)
    return email


async def toggle_star_email(db: AsyncSession, email_id: int) -> Email | None:
    """Toggle the starred state of an email."""
    result = await db.execute(select(Email).where(Email.id == email_id))
    email = result.scalar_one_or_none()
    if email:
        email.is_starred = not email.is_starred
        await db.commit()
        await db.refresh(email)
    return email


async def get_starred_emails(
    db: AsyncSession, limit: int = 50, offset: int = 0,
    user_id: int | None = None,
) -> list[Email]:
    """Get starred emails."""
    query = select(Email).where(Email.is_starred == True)
    if user_id is not None:
        query = query.where(Email.user_id == user_id)
    result = await db.execute(
        query.order_by(Email.timestamp.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def delete_old_emails(db: AsyncSession, days: int = 30, user_id: int | None = None) -> int:
    """Delete emails older than the specified number of days. Returns count of deleted emails."""
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)

    email_filter = Email.timestamp < cutoff
    if user_id is not None:
        email_filter = email_filter & (Email.user_id == user_id)

    old_email_ids = select(Email.id).where(email_filter)
    await db.execute(delete(Task).where(Task.email_id.in_(old_email_ids)))

    result = await db.execute(delete(Email).where(email_filter))
    deleted_count = result.rowcount
    await db.commit()
    return deleted_count


# --- Pipeline Run Tracking ---


async def create_pipeline_run(db: AsyncSession, user_id: int | None = None) -> PipelineRun:
    run = PipelineRun(user_id=user_id, status="QUEUED")
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


async def get_pipeline_run_by_id(db: AsyncSession, run_id: int) -> PipelineRun | None:
    result = await db.execute(select(PipelineRun).where(PipelineRun.id == run_id))
    return result.scalar_one_or_none()


async def get_latest_pipeline_run(db: AsyncSession, user_id: int | None = None) -> PipelineRun | None:
    query = select(PipelineRun)
    if user_id is not None:
        query = query.where(PipelineRun.user_id == user_id)
    result = await db.execute(query.order_by(PipelineRun.created_at.desc()))
    return result.scalars().first()


async def update_pipeline_run(
    db: AsyncSession,
    run_id: int,
    *,
    status: str | None = None,
    fetched_count: int | None = None,
    processed_count: int | None = None,
    skipped_count: int | None = None,
    failed_count: int | None = None,
    started_at: datetime.datetime | None = None,
    finished_at: datetime.datetime | None = None,
    error_message: str | None = None,
) -> PipelineRun | None:
    run = await get_pipeline_run_by_id(db, run_id)
    if not run:
        return None

    if status is not None:
        run.status = status
    if fetched_count is not None:
        run.fetched_count = fetched_count
    if processed_count is not None:
        run.processed_count = processed_count
    if skipped_count is not None:
        run.skipped_count = skipped_count
    if failed_count is not None:
        run.failed_count = failed_count
    if started_at is not None:
        run.started_at = started_at
    if finished_at is not None:
        run.finished_at = finished_at
    if error_message is not None:
        run.error_message = error_message

    await db.commit()
    await db.refresh(run)
    return run
