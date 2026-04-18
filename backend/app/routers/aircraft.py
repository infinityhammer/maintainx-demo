from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Aircraft
from app.schemas import (
    AircraftCreate,
    AircraftResponse,
    AircraftUpdate,
    AircraftStatus,
)

router = APIRouter(prefix="/aircraft", tags=["aircraft"])


@router.get("", response_model=list[AircraftResponse])
async def list_aircraft(
    status_filter: Optional[AircraftStatus] = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Aircraft).order_by(Aircraft.id)
    if status_filter is not None:
        stmt = stmt.where(Aircraft.status == status_filter)
    rows = (await db.execute(stmt)).scalars().all()
    return list(rows)


@router.get("/{aircraft_id}", response_model=AircraftResponse)
async def get_aircraft(aircraft_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(Aircraft, aircraft_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    return obj


@router.post("", response_model=AircraftResponse, status_code=status.HTTP_201_CREATED)
async def create_aircraft(payload: AircraftCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Aircraft).where(Aircraft.tail_number == payload.tail_number)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="tail_number already exists")

    obj = Aircraft(**payload.model_dump())
    db.add(obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="tail_number already exists")
    await db.refresh(obj)
    return obj


@router.patch("/{aircraft_id}", response_model=AircraftResponse)
async def update_aircraft(
    aircraft_id: int,
    payload: AircraftUpdate,
    db: AsyncSession = Depends(get_db),
):
    obj = await db.get(Aircraft, aircraft_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(obj, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="tail_number already exists")
    await db.refresh(obj)
    return obj


@router.delete("/{aircraft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_aircraft(aircraft_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(Aircraft, aircraft_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    await db.delete(obj)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
