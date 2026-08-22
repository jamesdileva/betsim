"""API router package: all /api endpoints registered here."""

from fastapi import APIRouter

from api.history import router as history_router
from api.parlay import router as parlay_router
from api.simulation import router as simulation_router
from api.strategies import router as strategies_router
from api.system_plays import router as system_plays_router

api_router = APIRouter(prefix="/api")
api_router.include_router(simulation_router)
api_router.include_router(strategies_router)
api_router.include_router(system_plays_router)
api_router.include_router(parlay_router)
api_router.include_router(history_router)

__all__ = ["api_router"]
