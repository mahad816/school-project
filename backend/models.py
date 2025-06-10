# backend/models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    role: str  # "teacher" | "student" | "parent"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # One teacher → many classes
    classes: List["Class"] = Relationship(back_populates="teacher")

class Class(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    join_code: str = Field(index=True, unique=True)
    teacher_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StudentClassLink(SQLModel, table=True):
    student_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    class_id: Optional[int] = Field(default=None, foreign_key="class.id", primary_key=True)
