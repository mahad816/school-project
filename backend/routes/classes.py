from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
import secrets
from typing import List

from models import Class
from database import get_session
from routes.auth import require_teacher

router = APIRouter(prefix="/classes", tags=["classes"])

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