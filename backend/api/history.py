"""History endpoints: browse and delete past simulation runs."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db
from crud.simulation import delete_simulation_run, list_run_summaries
from schemas.history import RunListResponse

router = APIRouter()


@router.get("/runs", response_model=RunListResponse)
def list_runs(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
):
    return RunListResponse(runs=list_run_summaries(db, limit=limit))


@router.delete("/runs/{run_id}", status_code=204)
def remove_run(run_id: int, db: Annotated[Session, Depends(get_db)]):
    if not delete_simulation_run(db, run_id):
        raise HTTPException(status_code=404, detail="Run not found")
