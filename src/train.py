import argparse
import sys
from pathlib import Path


# I add the project root to sys.path because this top-level trainer can be run
# directly, and I still want its imports to work from the project package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.train.model_paths import (
    ANOMALY_MODEL,
    CV_CNN_MODEL,
    NLP_MODEL,
    NLP_VECTORIZER,
    TABULAR_MODEL,
)


DEFAULT_CV_CSV = "data/processed/cv/labels.csv"
DEFAULT_SMS_DATASET = "data/SMSSpamCollection"
DEFAULT_TABULAR_DATASET = "data/processed/transactions/clean_validation.csv"
DEFAULT_ANOMALY_DATASET = "data/processed/transactions/clean_main.csv"


def _require_path(path_str, task_name):
    # I validate task input paths here so each training branch fails early with
    # a clear message if the expected dataset is missing.
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"{task_name} dataset not found at: {path}")
    return path


def train_cv(args):
    # I keep each training task in its own helper so this file can behave like
    # one unified command center for the whole project.
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
    return [str(model_path)]


def train_nlp(args):
    # I route NLP training through the project's SMS training helper because
    # this unified trainer should reuse existing project logic when possible.
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
    # I keep the tabular branch separate because the tabular model uses a
    # different dataset shape and training function from NLP or CV.
    from src.train.train_tabular_model import train_tabular_fraud_model

    dataset_path = _require_path(args.tabular_dataset, "Tabular")
    train_tabular_fraud_model(str(dataset_path))
    return [str(TABULAR_MODEL)]


def train_anomaly(args):
    # I keep anomaly training separate too because anomaly detection learns
    # normal behavior differently from supervised fraud classification.
    from src.train.train_anomaly_model import train_anomaly_detector

    dataset_path = _require_path(args.anomaly_dataset, "Anomaly")
    train_anomaly_detector(str(dataset_path))
    return [str(ANOMALY_MODEL)]


def run_task(task_name, args):
    # I use a task-to-function mapping so the CLI can choose a training branch
    # without a long chain of repeated if/elif statements.
    trainers = {
        "cv": train_cv,
        "nlp": train_nlp,
        "tabular": train_tabular,
        "anomaly": train_anomaly,
    }
    selected_trainer = trainers[task_name]
    result = selected_trainer(args)
    return result


def parse_args():
    # I expose all major training settings here so I can run one task or all
    # tasks from the command line without editing Python code each time.
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
    # I let --task all expand into every training branch because sometimes I
    # want one command to rebuild multiple artifacts for the whole project.
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
    if successes:
        for task_name, outputs in successes:
            print(f"{task_name.upper()}: success")
            for output in outputs:
                print(f"  - {output}")
    if failures:
        for task_name, message in failures:
            print(f"{task_name.upper()}: failed -> {message}")

    if failures and args.task == "all" and not successes:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
