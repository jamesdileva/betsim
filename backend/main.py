from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import api_router
from config import settings
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    scheduler = None
    if settings.theoddsapi_api_key:
        from services.pipeline import SchedulerService

        scheduler = SchedulerService()
        scheduler.start()
    try:
        yield
    finally:
        if scheduler is not None:
            scheduler.stop()


app = FastAPI(
    title="Betsim API",
    version="0.1.0",
    description="Monte Carlo betting simulator backend",
    lifespan=lifespan,
)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # vite dev server
        "null",  # packaged app loads the renderer from file://
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
