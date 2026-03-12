import datetime
from sqlalchemy import Boolean, String, Text, DateTime, Integer, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from backend.database.session import Base


class PriorityLevel(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    google_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    picture: Mapped[str | None] = mapped_column(Text, nullable=True)
    gmail_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    gmail_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    gmail_token_expiry: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    )

    emails: Mapped[list["Email"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class Email(Base):
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    gmail_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    sender: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(500))
    body: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(50), index=True)
    subcategory: Mapped[str | None] = mapped_column(String(50))
    priority: Mapped[str | None] = mapped_column(
        SAEnum(PriorityLevel), default=PriorityLevel.LOW
    )
    deadline: Mapped[datetime.date | None] = mapped_column()
    summary: Mapped[str | None] = mapped_column(Text)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None), index=True
    )
    embedding: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    user: Mapped["User | None"] = relationship(back_populates="emails")
    tasks: Mapped[list["Task"]] = relationship(back_populates="email", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Email id={self.id} subject={self.subject!r}>"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    count: Mapped[int] = mapped_column(Integer, default=0)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email_id: Mapped[int] = mapped_column(ForeignKey("emails.id", ondelete="CASCADE"))
    deadline: Mapped[datetime.date | None] = mapped_column()
    status: Mapped[str] = mapped_column(
        SAEnum(TaskStatus), default=TaskStatus.PENDING
    )
    priority: Mapped[str | None] = mapped_column(SAEnum(PriorityLevel))

    email: Mapped["Email"] = relationship(back_populates="tasks")
