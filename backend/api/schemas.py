import datetime
from pydantic import BaseModel, Field


class EmailBase(BaseModel):
    gmail_id: str
    sender: str
    subject: str
    body: str
    timestamp: datetime.datetime


class EmailCreate(EmailBase):
    pass


class EmailOut(EmailBase):
    id: int
    category: str | None = None
    subcategory: str | None = None
    priority: str | None = None
    deadline: datetime.date | None = None
    summary: str | None = None
    is_read: bool = False
    is_starred: bool = False

    model_config = {"from_attributes": True}


class CategoryOut(BaseModel):
    id: int
    name: str
    count: int

    model_config = {"from_attributes": True}


class TaskOut(BaseModel):
    id: int
    email_id: int
    deadline: datetime.date | None = None
    status: str
    priority: str | None = None

    model_config = {"from_attributes": True}


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class SearchResult(BaseModel):
    emails: list[EmailOut]


class PipelineStatus(BaseModel):
    status: str
    run_id: int | None = None
    processed: int = 0
    message: str = ""


class PipelineTriggerRequest(BaseModel):
    limit: int = Field(default=50, ge=1, le=500)


class PipelineRunOut(BaseModel):
    id: int
    status: str
    fetched_count: int = 0
    processed_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    started_at: datetime.datetime | None = None
    finished_at: datetime.datetime | None = None
    error_message: str | None = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    picture: str | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    user: UserOut


class StatsOverview(BaseModel):
    total: int = 0
    unread: int = 0
    high_priority: int = 0
    deadlines: int = 0
    starred: int = 0
