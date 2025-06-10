from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..models import Class, StudentClassLink
from ..db import get_session
from routes.auth import require_student

router = APIRouter()

class JoinClassIn(BaseModel):
    join_code: str

@router.post("/classes/join", status_code=200)
async def join_class(
    payload: JoinClassIn,
    user=Depends(require_student),
    session: AsyncSession = Depends(get_session),
):
    # Find the class with the given join code
    result = await session.execute(
        select(Class).where(Class.join_code == payload.join_code)
    )
    cls = result.scalar_one_or_none()
    
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    # Check if student is already enrolled
    existing_link = await session.execute(
        select(StudentClassLink).where(
            StudentClassLink.student_id == user["id"],
            StudentClassLink.class_id == cls.id
        )
    )
    if existing_link.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this class"
        )
    
    # Create the enrollment link
    link = StudentClassLink(student_id=user["id"], class_id=cls.id)
    session.add(link)
    await session.commit()
    
    return {"message": "Successfully joined class"}

@router.get("/classes", response_model=List[Class])
async def get_student_classes(
    user=Depends(require_student),
    session: AsyncSession = Depends(get_session)
):
    # Get all classes the student is enrolled in
    result = await session.execute(
        select(Class)
        .join(StudentClassLink)
        .where(StudentClassLink.student_id == user["id"])
    )
    return result.scalars().all() 