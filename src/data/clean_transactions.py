import argparse
import os
import shutil

import pandas as pd


# I define shared paths once here because this file is responsible for turning
# raw transaction CSV files into the cleaned files used by the rest of the project.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_BASE_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "transactions")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "transactions")

DEFAULT_MAIN_INPUT = os.path.join(RAW_BASE_PATH, "financial_fraud_detection_dataset.csv")
DEFAULT_VALIDATION_INPUT = os.path.join(RAW_BASE_PATH, "card_transdata.csv")

DEFAULT_MAIN_OUTPUT = os.path.join(OUTPUT_PATH, "clean_main.csv")
DEFAULT_VALIDATION_OUTPUT = os.path.join(OUTPUT_PATH, "clean_validation.csv")

DEFAULT_SYNC_MAIN = os.path.join(PROJECT_ROOT, "data", "financial_fraud_detection_dataset 2.csv")
DEFAULT_SYNC_VALIDATION = os.path.join(PROJECT_ROOT, "data", "card_transdata.csv")


def sync_output_file(source_path, target_path):
    # I sync files back into the project-level data paths because some older
    # parts of the project still expect cleaned files in those locations.
    source_path = os.path.abspath(str(source_path))
    target_path = os.path.abspath(str(target_path))
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    if os.path.exists(target_path) or os.path.islink(target_path):
        os.unlink(target_path)

    try:
        # I try a hard link first because it is fast and avoids duplicating data.
        os.link(source_path, target_path)
        return "hardlink"
    except Exception:
        try:
            # I fall back to a symlink when a hard link is not possible.
            os.symlink(source_path, target_path)
            return "symlink"
        except Exception:
            # I copy only as a last resort so the sync still succeeds on systems
            # where linking is restricted.
            shutil.copyfile(source_path, target_path)
            return "copy"


def standardize_target(df):
    # I standardize labels here because the project uses more than one fraud
    # target name across datasets, but later stages need one shared label name.
    df = df.copy()
    if "fraud" in df.columns and "is_fraud" not in df.columns:
        df = df.rename(columns={"fraud": "is_fraud"})

    if "is_fraud" not in df.columns:
        raise ValueError("Dataset must contain either 'is_fraud' or 'fraud'.")

    # I handle both numeric labels and True/False style text here because the
    # transaction files in this project do not always store the target the same way.
    fraud_values = df["is_fraud"].astype(str).str.strip().str.lower()
    fraud_values = fraud_values.replace(
        {
            "true": 1,
            "false": 0,
            "yes": 1,
            "no": 0,
        }
    )

    fraud_series = pd.to_numeric(fraud_values, errors="coerce")
    df["is_fraud"] = fraud_series
    df = df.dropna(subset=["is_fraud"]).copy()
    df["is_fraud"] = df["is_fraud"].astype(int)
    return df


def drop_sparse_columns(df, threshold=0.9):
    # I drop very sparse columns because columns with too many missing values
    # often add more noise than useful learning signal in an early model.
    missing_ratio = df.isnull().mean()
    cols_to_keep = []

    for column_name, ratio in missing_ratio.items():
        if ratio < threshold:
            cols_to_keep.append(column_name)

    dropped_columns = sorted(set(df.columns) - set(cols_to_keep))
    cleaned_df = df[cols_to_keep].copy()
    return cleaned_df, dropped_columns


def fill_missing_values(df):
    # I fill numeric and categorical columns differently because numbers and
    # text columns need different strategies to remain sensible.
    df = df.copy()
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()

    for column_name in numeric_columns:
        median_value = df[column_name].median()
        df[column_name] = df[column_name].fillna(median_value)

    for column_name in categorical_columns:
        df[column_name] = df[column_name].fillna("missing")

    return df, numeric_columns, categorical_columns


def convert_timestamp_columns(df):
    # I convert time-like text columns into datetime objects here so later
    # scripts can sort, split, or engineer time-based features correctly.
    df = df.copy()
    converted_columns = []
    for column_name in df.columns:
        lowered_name = column_name.lower()

        if "time" in lowered_name or lowered_name == "timestamp":
            converted = pd.to_datetime(df[column_name], errors="coerce")
            if converted.notna().sum() > 0:
                df[column_name] = converted
                converted_columns.append(column_name)
    return df, converted_columns


def clean_single_dataset(input_path, sparse_threshold=0.9):
    # I keep single-dataset cleaning in its own function so I can apply the
    # same rules to both main and validation datasets.
    df = pd.read_csv(input_path)
    original_shape = df.shape

    df = standardize_target(df)
    df, dropped_columns = drop_sparse_columns(df, threshold=sparse_threshold)
    df, numeric_columns, categorical_columns = fill_missing_values(df)
    df, converted_timestamp_columns = convert_timestamp_columns(df)

    label_distribution = df["is_fraud"].value_counts(dropna=False).to_dict()

    summary = {}
    summary["input_path"] = str(input_path)
    summary["original_shape"] = original_shape
    summary["clean_shape"] = df.shape
    summary["dropped_columns"] = dropped_columns
    summary["numeric_columns"] = numeric_columns
    summary["categorical_columns"] = categorical_columns
    summary["timestamp_columns"] = converted_timestamp_columns
    summary["label_distribution"] = label_distribution
    return df, summary


def clean_transactions(
    main_input=DEFAULT_MAIN_INPUT,
    validation_input=DEFAULT_VALIDATION_INPUT,
    main_output=DEFAULT_MAIN_OUTPUT,
    validation_output=DEFAULT_VALIDATION_OUTPUT,
    sync_main_output=DEFAULT_SYNC_MAIN,
    sync_validation_output=DEFAULT_SYNC_VALIDATION,
    sparse_threshold=0.9,
    sync_project_paths=True,
):
    # I use one orchestration function here because the project needs both
    # transaction datasets cleaned in a consistent way before training.
    main_input = str(main_input)
    validation_input = str(validation_input)
    main_output = str(main_output)
    validation_output = str(validation_output)

    if not os.path.exists(main_input):
        raise FileNotFoundError(f"Main transaction dataset not found at: {main_input}")
    if not os.path.exists(validation_input):
        raise FileNotFoundError(f"Validation transaction dataset not found at: {validation_input}")

    os.makedirs(OUTPUT_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(main_output), exist_ok=True)
    os.makedirs(os.path.dirname(validation_output), exist_ok=True)

    df_main, main_summary = clean_single_dataset(main_input, sparse_threshold=sparse_threshold)
    df_val, validation_summary = clean_single_dataset(validation_input, sparse_threshold=sparse_threshold)

    df_main.to_csv(main_output, index=False)
    df_val.to_csv(validation_output, index=False)

    synced_outputs = []
    if sync_project_paths:
        main_sync_mode = sync_output_file(main_output, sync_main_output)
        validation_sync_mode = sync_output_file(validation_output, sync_validation_output)
        synced_outputs = []
        synced_outputs.append(f"{sync_main_output} ({main_sync_mode})")
        synced_outputs.append(f"{sync_validation_output} ({validation_sync_mode})")

    result = {}
    result["main_output"] = str(main_output)
    result["validation_output"] = str(validation_output)
    result["synced_outputs"] = synced_outputs
    result["main_summary"] = main_summary
    result["validation_summary"] = validation_summary
    return result


def print_summary(result):
    # I print a structured summary because data-cleaning is much easier to
    # verify when I can see shapes, drops, and label counts immediately.
    print("\nI finished cleaning the transaction datasets.")
    print(f"Main cleaned file: {result['main_output']}")
    print(f"Validation cleaned file: {result['validation_output']}")

    if result["synced_outputs"]:
        print("I also synced these project paths:")
        for output in result["synced_outputs"]:
            print(f"  - {output}")

    for name, summary in (
        ("MAIN", result["main_summary"]),
        ("VALIDATION", result["validation_summary"]),
    ):
        print(f"\n{name} DATASET")
        print(f"  Input: {summary['input_path']}")
        print(f"  Original shape: {summary['original_shape']}")
        print(f"  Clean shape: {summary['clean_shape']}")
        print(f"  Dropped sparse columns: {len(summary['dropped_columns'])}")
        print(f"  Timestamp columns converted: {summary['timestamp_columns']}")
        print(f"  Label distribution: {summary['label_distribution']}")


def parse_args():
    # I expose command-line arguments here so I can rerun cleaning with
    # different paths or thresholds without editing the script.
    parser = argparse.ArgumentParser(
        description="Clean and align transaction datasets for the fraud project."
    )
    parser.add_argument("--main-input", default=str(DEFAULT_MAIN_INPUT))
    parser.add_argument("--validation-input", default=str(DEFAULT_VALIDATION_INPUT))
    parser.add_argument("--main-output", default=str(DEFAULT_MAIN_OUTPUT))
    parser.add_argument("--validation-output", default=str(DEFAULT_VALIDATION_OUTPUT))
    parser.add_argument("--sparse-threshold", type=float, default=0.9)
    parser.add_argument(
        "--no-sync-project-paths",
        action="store_true",
        help="Do not copy cleaned outputs into the root data/ paths used by the API and trainer.",
    )
    return parser.parse_args()


def main():
    # I keep the script entry point small so the real cleaning logic stays in
    # reusable functions that tests or other modules can call later.
    args = parse_args()
    result = clean_transactions(
        main_input=args.main_input,
        validation_input=args.validation_input,
        main_output=args.main_output,
        validation_output=args.validation_output,
        sparse_threshold=args.sparse_threshold,
        sync_project_paths=not args.no_sync_project_paths,
    )
    print_summary(result)


if __name__ == "__main__":
    main()
