from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from src.api.config import cfg

router = APIRouter(prefix="/analytics", tags=["analytics"])


class VisualizeIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # I use optional fields here because I want this route to be flexible:
    # it can use default project files or a custom path that I pass in.
    path: Optional[str] = None
    show_plot: bool = False
    output_path: Optional[str] = None


@router.post("/visualize")
def visualize(input: VisualizeIn):
    # I convert string paths into Path objects because Path makes file handling
    # clearer and safer than manually joining raw strings.
    input_path = Path(input.path) if input.path else cfg.card_csv
    out_path = Path(input.output_path) if input.output_path else cfg.risk_chart

    if not input_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"I could not find the input dataset at {input_path}.",
        )

    # I create the output folder first so saving the chart does not fail
    # simply because the directory is missing.
    out_path.parent.mkdir(parents=True, exist_ok=True)

    from src.api.visualization import visualize_my_risk

    visualize_my_risk(
        path=str(input_path),
        show_plot=input.show_plot,
        output_path=str(out_path),
    )
    return {"saved_to": str(out_path)}


class OutliersIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # I ask for a column and nickname here because this route is meant for
    # exploratory analysis, where I may want to inspect different datasets
    # and describe them in a human-friendly way.
    csv_path: Optional[str] = None
    column: str = Field(..., min_length=1)
    nickname: str = Field(..., min_length=1)


@router.post("/outliers")
def outliers(input: OutliersIn):
    # I fall back to the configured card dataset so this route still works
    # even when I do not pass a custom CSV path from the frontend or tests.
    path = input.csv_path or str(cfg.card_csv)
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"I could not find the CSV file at {dataset_path}.",
        )

    from src.features.profiler import find_my_outliers

    find_my_outliers(str(dataset_path), input.column, input.nickname)
    return {"status": "ok", "csv": path, "column": input.column}
