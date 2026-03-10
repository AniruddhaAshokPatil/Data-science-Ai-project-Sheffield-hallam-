from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from pathlib import Path

from backend.config import cfg

# Import your existing modules
# - visualization.py lives in src/backend
from backend.visualization import visualize_my_risk  # type: ignore

# - profiler.py lives in src
#   Import it as "profiler" by going one package up
import sys
sys.path.append(str(cfg.src_dir))
import profiler  # type: ignore

router = APIRouter(prefix="/analytics", tags=["analytics"])


class VisualizeIn(BaseModel):
    path: Optional[str] = None
    show_plot: bool = False
    output_path: Optional[str] = None


@router.post("/visualize")
def visualize(input: VisualizeIn):
    input_path = Path(input.path) if input.path else cfg.card_csv
    out_path = Path(input.output_path) if input.output_path else cfg.risk_chart

    out_path.parent.mkdir(parents=True, exist_ok=True)

    visualize_my_risk(
        path=str(input_path),
        show_plot=input.show_plot,
        output_path=str(out_path),
    )
    return {"saved_to": str(out_path)}


class OutliersIn(BaseModel):
    csv_path: Optional[str] = None
    column: str
    nickname: str


@router.post("/outliers")
def outliers(input: OutliersIn):
    path = input.csv_path or str(cfg.card_csv)
    # Call your existing helper; return a tiny summary
    # Note: find_my_outliers prints to console; here we just call it.
    profiler.find_my_outliers(path, input.column, input.nickname)
    return {"status": "ok", "csv": path, "column": input.column}