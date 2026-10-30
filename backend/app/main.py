"""MediSense API entry point. Also serves the frontend files."""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import Base, engine, SessionLocal
from .seed import seed
from .routers import inventory, insights, planner, sales

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    yield

app = FastAPI(title="MediSense API", lifespan=lifespan)
for r in (inventory.router, sales.router, insights.router, planner.router):
    app.include_router(r, prefix="/api")
app.mount("/", StaticFiles(directory=Path(__file__).resolve().parents[2] / "frontend", html=True), name="web")
