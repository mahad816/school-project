# backend/models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime, time

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    role: str  # "teacher" | "student" | "parent"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # One teacher → many classes
    classes: List["Class"] = Relationship(back_populates="teacher")
    # One student → many grades
    grades: List["Grade"] = Relationship(back_populates="student")

class Class(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    join_code: str = Field(index=True, unique=True)
    teacher_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    teacher: User = Relationship(back_populates="classes")
    assignments: List["Assignment"] = Relationship(back_populates="class_")
    timetable_entries: List["TimetableEntry"] = Relationship(back_populates="class_")

class StudentClassLink(SQLModel, table=True):
    student_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    class_id: Optional[int] = Field(default=None, foreign_key="class.id", primary_key=True)

class Assignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_id: int = Field(foreign_key="class.id")
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    class_: Class = Relationship(back_populates="assignments")
    grades: List["Grade"] = Relationship(back_populates="assignment")

class TimetableEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_id: int = Field(foreign_key="class.id")
    day_of_week: int  # 0=Monday … 6=Sunday
    start_time: time
    end_time: time
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    class_: Class = Relationship(back_populates="timetable_entries")

class Grade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    assignment_id: int = Field(foreign_key="assignment.id")
    student_id: int = Field(foreign_key="user.id")
    score: float
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    assignment: Assignment = Relationship(back_populates="grades")
    student: User = Relationship(back_populates="grades")
