from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from ..models import Assignment, Class
from ..db import get_session
from routes.auth import require_teacher

router = APIRouter()

class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    class_id: int

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment: AssignmentCreate,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    # Verify the class belongs to the teacher
    result = await session.execute(
        select(Class).where(
            Class.id == assignment.class_id,
            Class.teacher_id == user["id"]
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found or you don't have permission"
        )
    
    new_assignment = Assignment(**assignment.dict())
    session.add(new_assignment)
    await session.commit()
    await session.refresh(new_assignment)
    return new_assignment

@router.get("/", response_model=List[Assignment])
async def get_assignments(
    class_id: Optional[int] = None,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    query = select(Assignment)
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
        query = query.where(Assignment.class_id == class_id)
    
    result = await session.execute(query)
    return result.scalars().all()

@router.get("/{assignment_id}", response_model=Assignment)
async def get_assignment(
    assignment_id: int,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Assignment)
        .join(Class)
        .where(
            Assignment.id == assignment_id,
            Class.teacher_id == user["id"]
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or you don't have permission"
        )
    return assignment

@router.patch("/{assignment_id}", response_model=Assignment)
async def update_assignment(
    assignment_id: int,
    assignment_update: AssignmentUpdate,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Assignment)
        .join(Class)
        .where(
            Assignment.id == assignment_id,
            Class.teacher_id == user["id"]
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or you don't have permission"
        )
    
    update_data = assignment_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(assignment, key, value)
    
    await session.commit()
    await session.refresh(assignment)
    return assignment

@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: int,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Assignment)
        .join(Class)
        .where(
            Assignment.id == assignment_id,
            Class.teacher_id == user["id"]
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or you don't have permission"
        )
    
    await session.delete(assignment)
    await session.commit() 