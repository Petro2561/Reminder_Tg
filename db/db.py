import enum
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional, Self, TypeAlias

from aiogram.enums import ChatType
from aiogram.types import Chat, User
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Time,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    registry,
    relationship,
)

Int16: TypeAlias = Annotated[int, 16]
Int64: TypeAlias = Annotated[int, 64]


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=func.now(),
        server_default=func.now(),
    )


class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            Int16: Integer,
            Int64: BigInteger,
            datetime: DateTime(timezone=True),
        }
    )


class DBUser(Base, TimestampMixin):
    __tablename__ = "users"

    user_id: Mapped[Int64] = mapped_column(
        BigInteger, unique=True, nullable=False, primary_key=True
    )
    username: Mapped[str] = mapped_column(unique=False, nullable=True)
    first_name: Mapped[str] = mapped_column(unique=False, nullable=True)
    second_name: Mapped[str] = mapped_column(unique=False, nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="user", cascade="all, delete-orphan"
    )
    utc_offset: Mapped[int] = mapped_column(default=3, nullable=True)

    @classmethod
    def from_aiogram(cls, user: User) -> Self:
        return cls(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            second_name=user.last_name,
        )

    def __str__(self):
        return f"{self.first_name}"


class RepeatType(enum.Enum):
    SINGLE = "single"
    WEEKLY = "weekly"
    DAILY = "daily"
    MONTH = "month"


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    date = Column(Date, nullable=True)
    time = Column(Time, nullable=False)
    repeat_type = Column(Enum(RepeatType), default=RepeatType.SINGLE)
    repeat_day_of_week = Column(String(20), nullable=True)
    user_id: Mapped[Int64] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    notified = Column(Boolean, default=False)

    user: Mapped["DBUser"] = relationship("DBUser", back_populates="reminders")

    @classmethod
    def from_gpt(cls, from_gpt: dict, user: DBUser) -> Self:
        date_str = from_gpt.get("дата", None)
        if date_str == "сегодня":
            date = datetime.now().date()  # Сегодняшняя дата
        else:
            date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
        repeat_type_map = {
            "еженедельно": RepeatType.WEEKLY,
            "ежедневно": RepeatType.DAILY,
            "одноразовое": RepeatType.SINGLE,
            "ежемесячно": RepeatType.MONTH,
        }
        repeat_type = repeat_type_map.get(
            from_gpt.get("тип_повторения", "").lower(), RepeatType.SINGLE
        )
        reminder_time = datetime.strptime(
            from_gpt.get("время", "09:00"), "%H:%M"
        ).time()
        reminder_datetime = datetime.combine(date, reminder_time) if date else None
        if reminder_datetime:
            reminder_datetime = reminder_datetime + (timedelta(hours=(3 - user.utc_offset)))

        return cls(
            title=from_gpt.get("событие", ""),
            date=date,
            time=reminder_datetime.time() if reminder_datetime else reminder_time,
            repeat_type=repeat_type,
            repeat_day_of_week=(
                from_gpt.get("день_недели", None)
                if repeat_type == RepeatType.WEEKLY
                else None
            ),
            user=user,
        )
