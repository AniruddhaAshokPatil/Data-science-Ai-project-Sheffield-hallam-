"""I use this file as one command-line entry point for all model training."""

import argparse
import sys
from pathlib import Path


# I add the project root to `sys.path` so I can run this file directly from
# the terminal and still import the rest of the project package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.train.model_paths import (  # noqa: E402
    ANOMALY_MODEL,
    CV_CNN_MODEL,
    NLP_MODEL,
    NLP_VECTORIZER,
    TABULAR_MODEL,
)


DEFAULT_CV_CSV = "data/processed/cv/labels.csv"
DEFAULT_SMS_DATASET = "data/raw/nlp/sms_spam.csv"
DEFAULT_TABULAR_DATASET = "data/raw/transactions/financial_fraud_detection_dataset.csv"
DEFAULT_ANOMALY_DATASET = "data/raw/transactions/financial_fraud_detection_dataset.csv"


def _require_path(path_str, task_name):
    # I validate each incoming path here so the script fails early with a
    # clear message when a dataset is missing.
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"{task_name} dataset not found at: {path}")
    return path


def train_cv(args):
    # I keep CV training in its own helper so the main flow stays readable.
    from src.train.train_cv_model import train_cv_model

    csv_path = _require_path(args.cv_csv, "CV")
    model_path = Path(args.cv_model_path)
    train_cv_model(
        csv_path=str(csv_path),
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        validation_split=args.validation_split,
        model_path=str(model_path),
        image_size=args.image_size,
    )
    metadata_path = model_path.with_suffix(".metadata.pkl")
    return [str(model_path), str(metadata_path)]


def train_nlp(args):
    # I reuse the SMS helper here because it already trains and saves the text
    # model in a way that fits the rest of this project.
    from src.api.smsspamcollection import run_sms_classifier

    dataset_path = _require_path(args.nlp_dataset, "NLP")
    save_dir = Path(args.nlp_save_dir)
    result = run_sms_classifier(
        path=str(dataset_path),
        verbose=True,
        save_dir=str(save_dir),
    )
    if result is None:
        raise RuntimeError("NLP training did not complete successfully.")
    return [str(save_dir / NLP_MODEL.name), str(save_dir / NLP_VECTORIZER.name)]


def train_tabular(args):
    # I keep the tabular branch separate because it uses structured features
    # instead of text or images.
    from src.train.train_tabular_model import train_tabular_fraud_model

    dataset_path = _require_path(args.tabular_dataset, "Tabular")
    train_tabular_fraud_model(str(dataset_path))
    return [str(TABULAR_MODEL)]


def train_anomaly(args):
    # I keep anomaly training separate too because it learns normal patterns
    # rather than direct fraud labels.
    from src.train.train_anomaly_model import train_anomaly_model

    dataset_path = _require_path(args.anomaly_dataset, "Anomaly")
    summary = train_anomaly_model(input_path=dataset_path)
    return [summary["model_path"], summary["metadata_path"]]


def run_task(task_name, args):
    # I use a dictionary here because it is simpler to read than a long series
    # of repeated `if` and `elif` checks.
    trainers = {
        "cv": train_cv,
        "nlp": train_nlp,
        "tabular": train_tabular,
        "anomaly": train_anomaly,
    }
    selected_trainer = trainers[task_name]
    return selected_trainer(args)


def parse_args():
    # I expose the common training settings here so I can run one pipeline or
    # all pipelines from the command line.
    parser = argparse.ArgumentParser(
        description="Unified trainer for the fraud detection project."
    )
    parser.add_argument(
        "--task",
        choices=["cv", "nlp", "tabular", "anomaly", "all"],
        default="cv",
        help="Which training pipeline to run.",
    )

    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--validation-split", type=float, default=0.2)
    parser.add_argument("--image-size", type=int, default=224)

    parser.add_argument("--cv-csv", default=DEFAULT_CV_CSV)
    parser.add_argument("--cv-model-path", default=str(CV_CNN_MODEL))

    parser.add_argument("--nlp-dataset", default=DEFAULT_SMS_DATASET)
    parser.add_argument("--nlp-save-dir", default=str(NLP_MODEL.parent))

    parser.add_argument("--tabular-dataset", default=DEFAULT_TABULAR_DATASET)
    parser.add_argument("--anomaly-dataset", default=DEFAULT_ANOMALY_DATASET)
    return parser.parse_args()


def main():
    # I let `--task all` expand into every training branch because that gives
    # me one rebuild command for the whole project.
    args = parse_args()
    if args.task == "all":
        tasks = ["cv", "nlp", "tabular", "anomaly"]
    else:
        tasks = [args.task]

    successes = []
    failures = []

    for task_name in tasks:
        print(f"\n=== Training: {task_name.upper()} ===")
        try:
            outputs = run_task(task_name, args)
            successes.append((task_name, outputs))
        except Exception as exc:
            failures.append((task_name, str(exc)))
            print(f"{task_name.upper()} failed: {exc}")
            if args.task != "all":
                raise

    print("\n=== Training Summary ===")
    for task_name, outputs in successes:
        print(f"{task_name.upper()}: success")
        for output in outputs:
            print(f"  - {output}")

    for task_name, message in failures:
        print(f"{task_name.upper()}: failed -> {message}")

    if failures and args.task == "all" and not successes:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
