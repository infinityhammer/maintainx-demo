from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Aircraft, WorkOrder
from app.schemas import (
    WorkOrderCreate,
    WorkOrderPriority,
    WorkOrderResponse,
    WorkOrderStatus,
    WorkOrderUpdate,
)

router = APIRouter(prefix="/work-orders", tags=["work-orders"])

# State machine: from -> {allowed nexts}.
# Cancel is allowed from any non-terminal state. Direct in_progress -> complete is
# allowed for quick fixes that did not require parts.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "open": {"in_progress", "cancelled"},
    "in_progress": {"awaiting_parts", "complete", "cancelled"},
    "awaiting_parts": {"in_progress", "complete", "cancelled"},
    "complete": set(),
    "cancelled": set(),
}


def _validate_transition(current: str, nxt: str) -> None:
    if current == nxt:
        return
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if nxt not in allowed:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status transition: {current} -> {nxt}",
        )


@router.get("", response_model=list[WorkOrderResponse])
async def list_work_orders(
    status_filter: Optional[WorkOrderStatus] = Query(default=None, alias="status"),
    aircraft_id: Optional[int] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(WorkOrder)
        .options(selectinload(WorkOrder.aircraft))
        .order_by(WorkOrder.id)
    )
    if status_filter is not None:
        stmt = stmt.where(WorkOrder.status == status_filter)
    if aircraft_id is not None:
        stmt = stmt.where(WorkOrder.aircraft_id == aircraft_id)
    rows = (await db.execute(stmt)).scalars().all()
    return list(rows)


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
async def get_work_order(work_order_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(WorkOrder)
        .options(selectinload(WorkOrder.aircraft))
        .where(WorkOrder.id == work_order_id)
    )
    obj = (await db.execute(stmt)).scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=404, detail="Work order not found")
    return obj


@router.post("", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_work_order(payload: WorkOrderCreate, db: AsyncSession = Depends(get_db)):
    aircraft = await db.get(Aircraft, payload.aircraft_id)
    if aircraft is None:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    obj = WorkOrder(**payload.model_dump())
    db.add(obj)
    await db.commit()

    stmt = (
        select(WorkOrder)
        .options(selectinload(WorkOrder.aircraft))
        .where(WorkOrder.id == obj.id)
    )
    return (await db.execute(stmt)).scalar_one()


@router.patch("/{work_order_id}", response_model=WorkOrderResponse)
async def update_work_order(
    work_order_id: int,
    payload: WorkOrderUpdate,
    db: AsyncSession = Depends(get_db),
):
    obj = await db.get(WorkOrder, work_order_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Work order not found")

    data = payload.model_dump(exclude_unset=True)

    if "status" in data and data["status"] is not None:
        _validate_transition(obj.status, data["status"])

    for field, value in data.items():
        setattr(obj, field, value)

    await db.commit()

    stmt = (
        select(WorkOrder)
        .options(selectinload(WorkOrder.aircraft))
        .where(WorkOrder.id == obj.id)
    )
    return (await db.execute(stmt)).scalar_one()


@router.delete("/{work_order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_order(work_order_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(WorkOrder, work_order_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Work order not found")
    await db.delete(obj)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
