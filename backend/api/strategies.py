"""Strategy CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db
from crud.strategy import (
    delete_strategy,
    get_strategy,
    list_strategies,
    save_strategy,
    update_strategy,
)
from schemas.strategy import StrategyCreate, StrategyRead, StrategyUpdate

router = APIRouter()


@router.get("/strategies", response_model=list[StrategyRead])
def list_all_strategies(db: Annotated[Session, Depends(get_db)]):
    return list_strategies(db)


@router.post("/strategies", response_model=StrategyRead, status_code=201)
def create_strategy(data: StrategyCreate, db: Annotated[Session, Depends(get_db)]):
    return save_strategy(db, data)


@router.get("/strategies/{strategy_id}", response_model=StrategyRead)
def read_strategy(strategy_id: int, db: Annotated[Session, Depends(get_db)]):
    strategy = get_strategy(db, strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.put("/strategies/{strategy_id}", response_model=StrategyRead)
def replace_strategy(
    strategy_id: int, data: StrategyUpdate, db: Annotated[Session, Depends(get_db)]
):
    updated = update_strategy(db, strategy_id, data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return updated


@router.delete("/strategies/{strategy_id}", status_code=204)
def remove_strategy(strategy_id: int, db: Annotated[Session, Depends(get_db)]):
    if not delete_strategy(db, strategy_id):
        raise HTTPException(status_code=404, detail="Strategy not found")

