from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

AircraftStatus = Literal["operational", "grounded", "maintenance"]
WorkOrderStatus = Literal[
    "open", "in_progress", "awaiting_parts", "complete", "cancelled"
]
WorkOrderPriority = Literal["low", "normal", "high", "critical"]


# ---------- Aircraft ----------

class AircraftBase(BaseModel):
    tail_number: str = Field(..., min_length=1, max_length=64)
    model: str = Field(..., min_length=1, max_length=128)
    squadron: str = Field(default="", max_length=128)
    status: AircraftStatus = "operational"


class AircraftCreate(AircraftBase):
    pass


class AircraftUpdate(BaseModel):
    tail_number: Optional[str] = Field(default=None, min_length=1, max_length=64)
    model: Optional[str] = Field(default=None, min_length=1, max_length=128)
    squadron: Optional[str] = Field(default=None, max_length=128)
    status: Optional[AircraftStatus] = None


class AircraftResponse(AircraftBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ---------- Work Order ----------

class WorkOrderBase(BaseModel):
    aircraft_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: WorkOrderPriority = "normal"
    status: WorkOrderStatus = "open"
    assigned_to: Optional[str] = Field(default=None, max_length=128)


class WorkOrderCreate(WorkOrderBase):
    pass


class WorkOrderUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[WorkOrderPriority] = None
    status: Optional[WorkOrderStatus] = None
    assigned_to: Optional[str] = Field(default=None, max_length=128)


class WorkOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    aircraft_id: int
    title: str
    description: Optional[str] = None
    priority: WorkOrderPriority
    status: WorkOrderStatus
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    aircraft: Optional[AircraftResponse] = None
