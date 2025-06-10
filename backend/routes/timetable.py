from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, validator
from datetime import time

from ..models import TimetableEntry, Class
from ..db import get_session
from routes.auth import require_teacher

router = APIRouter()

class TimetableEntryCreate(BaseModel):
    class_id: int
    day_of_week: int  # 0=Monday … 6=Sunday
    start_time: time
    end_time: time

    @validator('day_of_week')
    def validate_day_of_week(cls, v):
        if not 0 <= v <= 6:
            raise ValueError('day_of_week must be between 0 and 6')
        return v

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class TimetableEntryUpdate(BaseModel):
    day_of_week: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    @validator('day_of_week')
    def validate_day_of_week(cls, v):
        if v is not None and not 0 <= v <= 6:
            raise ValueError('day_of_week must be between 0 and 6')
        return v

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v is not None and 'start_time' in values and values['start_time'] is not None:
            if v <= values['start_time']:
                raise ValueError('end_time must be after start_time')
        return v

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_timetable_entry(
    entry: TimetableEntryCreate,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    # Verify the class belongs to the teacher
    result = await session.execute(
        select(Class).where(
            Class.id == entry.class_id,
            Class.teacher_id == user["id"]
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found or you don't have permission"
        )
    
    new_entry = TimetableEntry(**entry.dict())
    session.add(new_entry)
    await session.commit()
    await session.refresh(new_entry)
    return new_entry

@router.get("/", response_model=List[TimetableEntry])
async def get_timetable_entries(
    class_id: Optional[int] = None,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    query = select(TimetableEntry)
    if class_id:
        # Verify the class belongs to the teacher
        result = await session.execute(
            select(Class).where(
                Class.id == class_id,
                Class.teacher_id == user["id"]
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found or you don't have permission"
            )
        query = query.where(TimetableEntry.class_id == class_id)
    
    result = await session.execute(query)
    return result.scalars().all()

@router.get("/{entry_id}", response_model=TimetableEntry)
async def get_timetable_entry(
    entry_id: int,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(TimetableEntry)
        .join(Class)
        .where(
            TimetableEntry.id == entry_id,
            Class.teacher_id == user["id"]
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timetable entry not found or you don't have permission"
        )
    return entry

@router.patch("/{entry_id}", response_model=TimetableEntry)
async def update_timetable_entry(
    entry_id: int,
    entry_update: TimetableEntryUpdate,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(TimetableEntry)
        .join(Class)
        .where(
            TimetableEntry.id == entry_id,
            Class.teacher_id == user["id"]
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timetable entry not found or you don't have permission"
        )
    
    update_data = entry_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entry, key, value)
    
    await session.commit()
    await session.refresh(entry)
    return entry

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timetable_entry(
    entry_id: int,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(TimetableEntry)
        .join(Class)
        .where(
            TimetableEntry.id == entry_id,
            Class.teacher_id == user["id"]
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timetable entry not found or you don't have permission"
        )
    
    await session.delete(entry)
    await session.commit() 