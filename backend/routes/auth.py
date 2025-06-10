# backend/auth.py
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Literal

from passlib.hash import bcrypt
from jose import JWTError, jwt

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-.env")
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

# Simulated DB fetch (replace with real DB logic)
def get_user_by_username(username: str):
    # TODO: Replace with real DB lookup
    # Example user for demonstration
    if username == "stu1":
        return {"username": "stu1", "role": "student"}
    if username == "teach1":
        return {"username": "teach1", "role": "teacher"}
    return None

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

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        role = payload.get("role")  # If you store role in token
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_student(user: dict = Depends(get_current_user)):
    if user["role"] != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student access required")
    return user

def require_teacher(user: dict = Depends(get_current_user)):
    if user["role"] != "teacher":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher access required")
    return user

@router.post("/signup")
async def signup(user: UserCreate):
    # Here you would typically save the user to your database
    hashed_password = get_password_hash(user.password)
    # Save user to database (implement this)
    return {
        "message": "User created successfully",
        "username": user.username,
        "role": user.role
    }

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    # Here you would typically verify the user against your database
    # For now, we'll just create a token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/student-area")
async def student_area(user=Depends(require_student)):
    return {"message": f"Welcome, {user['username']} (student)!"}

@router.get("/teacher-area")
async def teacher_area(user=Depends(require_teacher)):
    return {"message": f"Welcome, {user['username']} (teacher)!"}
