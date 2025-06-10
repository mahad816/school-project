# backend/auth.py
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Literal

from passlib.hash import bcrypt
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models import User
from db import get_session

router = APIRouter(prefix="/auth", tags=["auth"])

# Use a consistent secret key for development
SECRET_KEY = "your-super-secret-key-for-development-only"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["teacher", "student", "parent"]

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

security = HTTPBearer()

def get_password_hash(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return {}

async def get_user_by_username(username: str, session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
):
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = await get_user_by_username(username, session)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_student(user: User = Depends(get_current_user)):
    if user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student access required")
    return user

def require_teacher(user: User = Depends(get_current_user)):
    if user.role != "teacher":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher access required")
    return user

@router.post("/signup")
async def signup(user: UserCreate, session: AsyncSession = Depends(get_session)):
    # Check if username already exists
    existing = await get_user_by_username(user.username, session)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return {
        "message": "User created successfully",
        "username": db_user.username,
        "role": db_user.role
    }

@router.post("/login", response_model=Token)
async def login(user: UserLogin, session: AsyncSession = Depends(get_session)):
    db_user = await get_user_by_username(user.username, session)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    access_token = create_access_token(
        data={
            "sub": db_user.username,
            "role": db_user.role
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/student-area")
async def student_area(user=Depends(require_student)):
    return {"message": f"Welcome, {user.username} (student)!"}

@router.get("/teacher-area")
async def teacher_area(user=Depends(require_teacher)):
    return {"message": f"Welcome, {user.username} (teacher)!"}
