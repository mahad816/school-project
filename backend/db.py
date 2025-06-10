# backend/db.py
from .models import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Use SQLite for development
DATABASE_URL = "sqlite+aiosqlite:///school.db"

# Create an async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

# Create a session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for getting a session
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
