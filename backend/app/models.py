from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Aircraft(Base):
    __tablename__ = "aircraft"

    id: Mapped[int] = mapped_column(primary_key=True)
    tail_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    squadron: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="operational")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    work_orders: Mapped[list["WorkOrder"]] = relationship(
        back_populates="aircraft",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    aircraft_id: Mapped[int] = mapped_column(
        ForeignKey("aircraft.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(16), nullable=False, default="normal")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    assigned_to: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    aircraft: Mapped["Aircraft"] = relationship(back_populates="work_orders", lazy="selectin")
