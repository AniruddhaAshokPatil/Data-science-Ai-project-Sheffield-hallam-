import argparse
import json
import os

import pandas as pd


# I build these default paths once at the top of the file so the script can be
# reused from the command line or tests without repeating the same locations.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "transactions")

DEFAULT_MAIN_INPUT = os.path.join(PROCESSED_DIR, "clean_main.csv")
DEFAULT_VALIDATION_INPUT = os.path.join(PROCESSED_DIR, "clean_validation.csv")
DEFAULT_MAIN_OUTPUT = os.path.join(PROCESSED_DIR, "encoded_main.csv")
DEFAULT_VALIDATION_OUTPUT = os.path.join(PROCESSED_DIR, "encoded_validation.csv")
DEFAULT_METADATA_OUTPUT = os.path.join(PROCESSED_DIR, "encoded_schema.json")

TARGET_COLUMN = "is_fraud"
# I drop these columns because they behave more like identifiers than useful
# model features, and they can make the model memorize instead of generalize.
DROP_COLUMNS = {
    "transaction_id",
    "sender_account",
    "receiver_account",
    "ip_address",
    "device_hash",
}
HIGH_CARDINALITY_THRESHOLD = 20


def _require_path(path_str, label):
    # I validate paths early so the script fails with a clear message before
    # I spend time reading or transforming data that is not there.
    path = str(path_str)

    if os.path.exists(path):
        return path

    raise FileNotFoundError(f"{label} dataset not found at: {path}")


def _standardize_target(df):
    # I standardize the target name because the project uses both "fraud" and
    # "is_fraud" in different datasets, but later training code needs one name.
    df = df.copy()
    if "fraud" in df.columns and TARGET_COLUMN not in df.columns:
        df = df.rename(columns={"fraud": TARGET_COLUMN})
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Dataset must contain '{TARGET_COLUMN}' or 'fraud'.")
    return df


def _convert_datetime_like_columns(df):
    # I convert time-like columns into numeric timestamps because most machine
    # learning models cannot learn directly from raw datetime strings.
    df = df.copy()
    converted_columns = []

    for column_name in df.columns:
        lowered_name = column_name.lower()

        if column_name == TARGET_COLUMN:
            continue
        if column_name in DROP_COLUMNS:
            continue
        if "time" not in lowered_name and "date" not in lowered_name:
            continue

        parsed = pd.to_datetime(df[column_name], errors="coerce")
        if parsed.notna().sum() == 0:
            continue

        # I convert to Unix seconds so all rows share one clean numeric time format.
        unix_seconds = parsed.astype("int64") // 10**9
        safe_seconds = unix_seconds.where(parsed.notna(), 0)
        df[column_name] = safe_seconds.astype("int64")
        converted_columns.append(column_name)

    return df, converted_columns


def _prepare_features(df):
    # I keep the preparation steps in one helper so both datasets go through
    # the same cleaning rules before I try to align their schemas.
    df = _standardize_target(df)
    drop_columns = []
    for column_name in DROP_COLUMNS:
        if column_name in df.columns:
            drop_columns.append(column_name)

    df = df.drop(columns=drop_columns)
    df, converted_datetime_columns = _convert_datetime_like_columns(df)
    return df, drop_columns, converted_datetime_columns


def _sort_feature_columns(columns):
    # I sort feature columns so saved outputs stay consistent across runs,
    # which makes debugging and training comparisons much easier for me.
    feature_columns = []

    for column_name in columns:
        if column_name != TARGET_COLUMN:
            feature_columns.append(column_name)

    feature_columns.sort()
    return feature_columns


def encode_transactions(
    main_input=DEFAULT_MAIN_INPUT,
    validation_input=DEFAULT_VALIDATION_INPUT,
    main_output=DEFAULT_MAIN_OUTPUT,
    validation_output=DEFAULT_VALIDATION_OUTPUT,
    metadata_output=DEFAULT_METADATA_OUTPUT,
):
    # I use one function for both datasets because the whole point of this file
    # is to encode them into a shared training-ready structure.
    main_input = _require_path(main_input, "Main")
    validation_input = _require_path(validation_input, "Validation")
    main_output = str(main_output)
    validation_output = str(validation_output)
    metadata_output = str(metadata_output)

    df_main = pd.read_csv(main_input)
    df_val = pd.read_csv(validation_input)

    df_main, main_dropped, main_datetime_columns = _prepare_features(df_main)
    df_val, validation_dropped, validation_datetime_columns = _prepare_features(df_val)

    y_main = pd.to_numeric(df_main.pop(TARGET_COLUMN), errors="coerce")
    y_main = y_main.fillna(0).astype(int)

    y_val = pd.to_numeric(df_val.pop(TARGET_COLUMN), errors="coerce")
    y_val = y_val.fillna(0).astype(int)

    # I concatenate both datasets before one-hot encoding so they end up with
    # the same categorical feature columns instead of drifting apart.
    combined = pd.concat(
        {
            "main": df_main,
            "validation": df_val,
        },
        names=["dataset"],
        sort=False,
    )

    categorical_columns = combined.select_dtypes(
        include=["object", "string", "category", "bool"]
    ).columns.tolist()
    low_cardinality_columns = []
    high_cardinality_columns = []

    # I split categorical columns by cardinality so I can avoid one-hot
    # encoding fields that would explode into too many sparse columns.
    for column_name in categorical_columns:
        unique_count = combined[column_name].nunique(dropna=False)
        if unique_count > HIGH_CARDINALITY_THRESHOLD:
            high_cardinality_columns.append(column_name)
        else:
            low_cardinality_columns.append(column_name)

    encoded = combined.copy()

    for column_name in high_cardinality_columns:
        # I use frequency encoding for higher-cardinality columns because it
        # keeps the feature space compact while still preserving signal.
        frequency_map = encoded[column_name].value_counts(normalize=True).to_dict()
        encoded[f"{column_name}_freq"] = encoded[column_name].map(frequency_map).fillna(0.0)

    if high_cardinality_columns:
        encoded = encoded.drop(columns=high_cardinality_columns)

    # I still use one-hot encoding for smaller categorical fields because the
    # resulting columns stay readable and beginner-friendly.
    encoded = pd.get_dummies(
        encoded,
        columns=low_cardinality_columns,
        dummy_na=False,
        dtype=int,
    )

    encoded_main = encoded.xs("main").copy()
    encoded_validation = encoded.xs("validation").copy()

    all_feature_columns = encoded_main.columns.union(encoded_validation.columns)
    ordered_feature_columns = _sort_feature_columns(all_feature_columns)
    encoded_main = encoded_main.reindex(columns=ordered_feature_columns, fill_value=0)
    encoded_validation = encoded_validation.reindex(columns=ordered_feature_columns, fill_value=0)

    encoded_main[TARGET_COLUMN] = y_main.to_numpy()
    encoded_validation[TARGET_COLUMN] = y_val.to_numpy()

    # I create output folders before saving so file writes do not fail just
    # because the target directory does not exist yet.
    os.makedirs(os.path.dirname(main_output), exist_ok=True)
    os.makedirs(os.path.dirname(validation_output), exist_ok=True)
    os.makedirs(os.path.dirname(metadata_output), exist_ok=True)
    encoded_main.to_csv(main_output, index=False)
    encoded_validation.to_csv(validation_output, index=False)

    metadata = {}
    metadata["target_column"] = TARGET_COLUMN
    metadata["feature_columns"] = ordered_feature_columns
    metadata["categorical_columns_encoded"] = categorical_columns
    metadata["low_cardinality_columns"] = low_cardinality_columns
    metadata["high_cardinality_columns"] = high_cardinality_columns
    metadata["main_dropped_columns"] = main_dropped
    metadata["validation_dropped_columns"] = validation_dropped
    metadata["main_datetime_columns"] = main_datetime_columns
    metadata["validation_datetime_columns"] = validation_datetime_columns
    metadata["main_output"] = str(main_output)
    metadata["validation_output"] = str(validation_output)
    with open(metadata_output, "w", encoding="utf-8") as file:
        file.write(json.dumps(metadata, indent=2))

    result = {}
    result["main_output"] = str(main_output)
    result["validation_output"] = str(validation_output)
    result["metadata_output"] = str(metadata_output)
    result["main_shape"] = encoded_main.shape
    result["validation_shape"] = encoded_validation.shape
    result["categorical_columns_encoded"] = categorical_columns
    result["feature_columns"] = ordered_feature_columns
    result["main_dropped_columns"] = main_dropped
    result["validation_dropped_columns"] = validation_dropped
    result["main_datetime_columns"] = main_datetime_columns
    result["validation_datetime_columns"] = validation_datetime_columns
    result["low_cardinality_columns"] = low_cardinality_columns
    result["high_cardinality_columns"] = high_cardinality_columns
    return result


def print_summary(result):
    # I keep a readable summary function because data-prep scripts are easier
    # to trust when I can quickly see what they produced.
    print("Datasets encoded successfully.")
    print(f"Main saved to: {result['main_output']}")
    print(f"Validation saved to: {result['validation_output']}")
    print(f"Schema saved to: {result['metadata_output']}")
    print(f"Main shape: {result['main_shape']}")
    print(f"Validation shape: {result['validation_shape']}")
    print(f"Feature count: {len(result['feature_columns'])}")
    print(f"Encoded categorical columns: {result['categorical_columns_encoded']}")
    print(f"Low-cardinality one-hot columns: {result['low_cardinality_columns']}")
    print(f"High-cardinality frequency columns: {result['high_cardinality_columns']}")
    print(f"Main dropped columns: {result['main_dropped_columns']}")
    print(f"Validation dropped columns: {result['validation_dropped_columns']}")
    print(f"Main datetime columns converted: {result['main_datetime_columns']}")
    print(f"Validation datetime columns converted: {result['validation_datetime_columns']}")


def parse_args():
    # I use argparse so I can run this file as a script with custom paths
    # without editing the Python code itself every time.
    parser = argparse.ArgumentParser(description="Encode cleaned transaction datasets for model training.")
    parser.add_argument("--main-input", default=str(DEFAULT_MAIN_INPUT))
    parser.add_argument("--validation-input", default=str(DEFAULT_VALIDATION_INPUT))
    parser.add_argument("--main-output", default=str(DEFAULT_MAIN_OUTPUT))
    parser.add_argument("--validation-output", default=str(DEFAULT_VALIDATION_OUTPUT))
    parser.add_argument("--metadata-output", default=str(DEFAULT_METADATA_OUTPUT))
    return parser.parse_args()


def main():
    # I keep a small main function so this file works both as an importable
    # module and as a standalone script from the terminal.
    args = parse_args()
    result = encode_transactions(
        main_input=args.main_input,
        validation_input=args.validation_input,
        main_output=args.main_output,
        validation_output=args.validation_output,
        metadata_output=args.metadata_output,
    )
    print_summary(result)


if __name__ == "__main__":
    main()
