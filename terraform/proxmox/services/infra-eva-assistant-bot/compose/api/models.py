from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    telegram_username: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(Text, nullable=False, default="Europe/Madrid")
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    reminders = relationship("Reminder", back_populates="user")


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    task_text: Mapped[str] = mapped_column(Text, nullable=False)
    remind_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="scheduled")

    recurrence_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    recurrence_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    weekdays_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    remind_if_no_response: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    retry_delay_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cancel_on_event_type: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_persistent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    repeat_every_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stop_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    awaiting_ack: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    last_sent_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acked_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expired_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ack_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)  # contexto adicional del usuario
    url: Mapped[str | None] = mapped_column(Text, nullable=True)  # URL asociada a la tarea
    priority: Mapped[str | None] = mapped_column(Text, nullable=True, default="P3")  # P0-P4
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # descripción WYSIWYG HTML
    focalboard_card_id: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    focalboard_synced_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sent_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="reminders")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    event_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(Text, nullable=False, default="system")
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(Text, nullable=False, default="chat")
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)