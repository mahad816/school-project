from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel
from .db import engine
from .routes.auth import router as auth_router
from .routes.classes import router as classes_router
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(classes_router)

@app.on_event("startup")
async def on_startup():
    try:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise HTTPException(status_code=500, detail="Database initialization failed")

@app.get("/")
async def root():
    return {"message": "Welcome to the School Application API"}

