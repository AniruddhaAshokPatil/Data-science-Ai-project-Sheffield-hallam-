from pathlib import Path
import sys

# Ensure the directory containing this script is on sys.path for sibling imports.
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

from outline_detection import find_my_outliers
from visualization import visualize_my_risk

project_root = backend_dir.parent.parent
card_data_path = project_root / "data" / "card_transdata.csv"
financial_data_path = project_root / "data" / "financial_fraud_detection_dataset 2.csv"
output_dir = backend_dir / "outputs"
output_dir.mkdir(parents=True, exist_ok=True)
chart_output_path = output_dir / "risk_visualization.png"

find_my_outliers(
    str(card_data_path),
    "ratio_to_median_purchase_price",
    "Card Transaction Data"
)

find_my_outliers(
    str(financial_data_path),
    "spending_deviation_score",
    "Financial Fraud Data"
)

visualize_my_risk(str(card_data_path), output_path=str(chart_output_path))
