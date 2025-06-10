from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
import secrets
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Class
from ..db import get_session
from routes.auth import require_teacher

router = APIRouter(prefix="/classes", tags=["classes"])

@router.get("/", response_model=List[Class])
async def get_classes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Class))
    return result.scalars().all()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_class(
    name: str,
    user=Depends(require_teacher),
    session=Depends(get_session)
):
    join_code = secrets.token_urlsafe(6)
    new_class = Class(name=name, join_code=join_code, teacher_id=user["id"])
    session.add(new_class)
    await session.commit()
    await session.refresh(new_class)
    return {"id": new_class.id, "join_code": join_code} 