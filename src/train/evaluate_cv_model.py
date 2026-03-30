import json
import os
from pathlib import Path

import pandas as pd

# I set these runtime flags before importing torch because some local shells
# trip over OpenMP defaults even though the model code itself is fine.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import torch
from sklearn.metrics import confusion_matrix, precision_score, recall_score
from torch.utils.data import DataLoader
from torchvision import transforms

from src.data.dataset import CVDataset
from src.train.load_models import load_cv_model
from src.train.model_paths import CV_CNN_MODEL


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LABELS = PROJECT_ROOT / "data" / "processed" / "cv" / "labels.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "cv_evaluation.json"


EVAL_TRANSFORM = transforms.Compose(
    [
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)


def evaluate_cv_model(labels_path: Path = DEFAULT_LABELS, output_path: Path = DEFAULT_OUTPUT):
    # I keep this evaluator focused on the saved CV artifact so I can prove
    # the training path produces something the API can load and score.
    labels_path = Path(labels_path)
    output_path = Path(output_path)

    if not labels_path.exists():
        raise FileNotFoundError(f"Labels file not found at: {labels_path}")
    if not Path(CV_CNN_MODEL).exists():
        raise FileNotFoundError(f"CV model artifact not found at: {CV_CNN_MODEL}")

    labels = pd.read_csv(labels_path)
    if "split" in labels.columns:
        labels = labels[labels["split"] == "test"].reset_index(drop=True)

    dataset = CVDataset(labels, transform=EVAL_TRANSFORM)
    loader = DataLoader(dataset, batch_size=16)
    model = load_cv_model()

    correct = 0
    total = 0
    predicted_labels = []
    true_labels = []
    with torch.no_grad():
        for images, targets in loader:
            logits = model(images)
            probs = torch.sigmoid(logits)
            preds = (probs > 0.5).float().view(-1)
            correct += int((preds == targets).sum().item())
            total += int(targets.numel())
            predicted_labels.extend(preds.int().tolist())
            true_labels.extend(targets.int().tolist())

    tn, fp, fn, tp = confusion_matrix(true_labels, predicted_labels, labels=[0, 1]).ravel()

    summary = {
        "rows_evaluated": total,
        "accuracy": float(correct / total) if total else 0.0,
        "precision": float(precision_score(true_labels, predicted_labels, zero_division=0)),
        "recall": float(recall_score(true_labels, predicted_labels, zero_division=0)),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
    }
    output_path.write_text(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    print(json.dumps(evaluate_cv_model(), indent=2))
