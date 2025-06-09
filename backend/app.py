from fastapi import FastAPI
from sqlmodel import SQLModel
from db import engine
from routes.auth import router as auth_router

app = FastAPI()

# Include the auth router
app.include_router(auth_router)

@app.on_event("startup")
async def on_startup():
    try:
        # Creates all tables for models you've imported
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    except Exception as e:
        print(f"Error during startup: {e}")

@app.get("/")
async def root():
    return {"status": "ok"}

