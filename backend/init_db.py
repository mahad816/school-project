import asyncio
from db import init_db, get_session
from models import User
from passlib.hash import bcrypt

def get_password_hash(password: str) -> str:
    return bcrypt.hash(password)

async def create_test_users():
    async for session in get_session():
        # Create test teacher
        teacher = User(
            username="teacher1",
            hashed_password=get_password_hash("password123"),
            role="teacher"
        )
        session.add(teacher)

        # Create test student
        student = User(
            username="student1",
            hashed_password=get_password_hash("password123"),
            role="student"
        )
        session.add(student)

        await session.commit()
        break  # Only need one session

async def main():
    # Initialize database
    await init_db()
    # Create test users
    await create_test_users()
    print("Database initialized with test users!")

if __name__ == "__main__":
    asyncio.run(main()) 