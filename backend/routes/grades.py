from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, validator
from datetime import datetime

from ..models import Grade, Assignment, Class
from ..db import get_session
from routes.auth import require_teacher

router = APIRouter()

class GradeCreate(BaseModel):
    assignment_id: int
    student_id: int
    score: float
    feedback: Optional[str] = None

    @validator('score')
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('score must be between 0 and 100')
        return v

class GradeUpdate(BaseModel):
    score: Optional[float] = None
    feedback: Optional[str] = None

    @validator('score')
    def validate_score(cls, v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError('score must be between 0 and 100')
        return v

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_grade(
    grade: GradeCreate,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    # Verify the assignment belongs to a class taught by the teacher
    result = await session.execute(
        select(Assignment)
        .join(Class)
        .where(
            Assignment.id == grade.assignment_id,
            Class.teacher_id == user["id"]
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or you don't have permission"
        )
    
    new_grade = Grade(**grade.dict())
    session.add(new_grade)
    await session.commit()
    await session.refresh(new_grade)
    return new_grade

@router.get("/", response_model=List[Grade])
async def get_grades(
    assignment_id: Optional[int] = None,
    student_id: Optional[int] = None,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    query = select(Grade)
    
    if assignment_id:
        # Verify the assignment belongs to a class taught by the teacher
        result = await session.execute(
            select(Assignment)
            .join(Class)
            .where(
                Assignment.id == assignment_id,
                Class.teacher_id == user["id"]
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found or you don't have permission"
            )
        query = query.where(Grade.assignment_id == assignment_id)
    
    if student_id:
        query = query.where(Grade.student_id == student_id)
    
    result = await session.execute(query)
    return result.scalars().all()

@router.get("/{grade_id}", response_model=Grade)
async def get_grade(
    grade_id: int,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Grade)
        .join(Assignment)
        .join(Class)
        .where(
            Grade.id == grade_id,
            Class.teacher_id == user["id"]
        )
    )
    grade = result.scalar_one_or_none()
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found or you don't have permission"
        )
    return grade

@router.patch("/{grade_id}", response_model=Grade)
async def update_grade(
    grade_id: int,
    grade_update: GradeUpdate,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Grade)
        .join(Assignment)
        .join(Class)
        .where(
            Grade.id == grade_id,
            Class.teacher_id == user["id"]
        )
    )
    grade = result.scalar_one_or_none()
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found or you don't have permission"
        )
    
    update_data = grade_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(grade, key, value)
    
    grade.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(grade)
    return grade

@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grade(
    grade_id: int,
    user=Depends(require_teacher),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Grade)
        .join(Assignment)
        .join(Class)
        .where(
            Grade.id == grade_id,
            Class.teacher_id == user["id"]
        )
    )
    grade = result.scalar_one_or_none()
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found or you don't have permission"
        )
    
    await session.delete(grade)
    await session.commit() 