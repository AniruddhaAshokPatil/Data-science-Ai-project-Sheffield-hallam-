import csv
import os
import pickle
import re

import pandas as pd

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.model_selection import train_test_split
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "I need scikit-learn for this file. I can install it with: pip install scikit-learn"
    ) from exc


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# I keep the paths at the top because this script is one complete NLP pipeline
# from raw SMS messages to saved machine-learning files.
RAW_INPUT_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "nlp", "claim_email_ham_spam.csv")
CLEAN_INPUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "nlp", "claim_email_ham_spam.tsv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "nlp")


def normalize_message(text):
    # I normalize message text here because messy quotes, commas, and spacing
    # can make parsing inconsistent before I even reach model preprocessing.
    text = str(text)
    text = text.replace('""', '"')
    text = text.strip()
    text = text.strip('"')
    text = text.replace('"', "")
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r",\s*,+", ",", text)
    text = re.sub(r"\s+", " ", text).strip(" ,")
    return text


def parse_raw_sms_dataset(path):
    # I keep a manual parser here because some SMS dataset files can contain
    # awkward formatting that is not reliably handled by one simple read_csv call.
    records = []
    current_label = None
    current_message_parts = []

    with open(path, "r", encoding="utf-8", errors="replace") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line:
                continue

            match = re.match(r"^(ham|spam)\s*,\s*(.*)$", line, flags=re.IGNORECASE)
            if match:
                # I save the previous record before starting a new one because
                # some messages may span multiple raw lines in the source file.
                if current_label is not None:
                    records.append(
                        {
                            "label": current_label,
                            "message": normalize_message(" ".join(current_message_parts)),
                        }
                    )
                current_label = match.group(1).lower()
                current_message_parts = [match.group(2)]
            elif current_label is not None:
                current_message_parts.append(line)

    if current_label is not None:
        records.append(
            {
                "label": current_label,
                "message": normalize_message(" ".join(current_message_parts)),
            }
        )

    if not records:
        raise ValueError(f"Unable to parse dataset at {path}")

    return pd.DataFrame(records)


def load_sms_dataset(path):
    if path.lower().endswith(".csv"):
        csv_df = pd.read_csv(path)
        lowered_columns = {column.lower(): column for column in csv_df.columns}

        if {"label", "body"}.issubset(lowered_columns):
            label_column = lowered_columns["label"]
            body_column = lowered_columns["body"]
            subject_column = lowered_columns.get("subject")

            if subject_column:
                message_series = (
                    csv_df[subject_column].fillna("").astype(str).str.strip() + " " + csv_df[body_column].fillna("").astype(str)
                ).str.strip()
            else:
                message_series = csv_df[body_column].fillna("").astype(str)

            dataset = pd.DataFrame(
                {
                    "label": csv_df[label_column].astype(str).str.strip().str.lower(),
                    "message": message_series.map(normalize_message),
                }
            )
            dataset = dataset[dataset["label"].isin({"ham", "spam"})].reset_index(drop=True)
            if not dataset.empty:
                return dataset

    # I try more than one read option here because public SMS datasets often
    # appear in slightly different separators or quoting styles.
    read_options = [
        {"sep": "\t", "header": None, "names": ["label", "message"]},
        {"sep": ",", "header": None, "names": ["label", "message"]},
    ]

    for options in read_options:
        try:
            df = pd.read_csv(path, **options)
        except pd.errors.ParserError:
            continue

        if "label" in df.columns and "message" in df.columns:
            df["label"] = df["label"].astype(str).str.strip().str.strip('"').str.lower()
            df["message"] = df["message"].map(normalize_message)
            if df["label"].isin({"ham", "spam"}).all():
                return df

    # I fall back to the manual parser only if the simpler CSV reads fail.
    return parse_raw_sms_dataset(path)


def export_clean_sms_dataset(source_path=RAW_INPUT_PATH, output_path=CLEAN_INPUT_PATH):
    # I export a clean tab-separated corpus file because other parts of the project
    # expect a stable text dataset for training and API startup.
    df = load_sms_dataset(source_path)
    output_folder = os.path.dirname(output_path)
    os.makedirs(output_folder, exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t", quoting=csv.QUOTE_MINIMAL)

        for row in df.itertuples(index=False):
            label = row.label
            message = row.message
            writer.writerow([label, message])

    return df


def clean_text(text):
    # I lower-case and strip noisy patterns here because NLP models usually
    # work better when text is cleaned into a simpler, more consistent form.
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    # I create the clean corpus first if it is missing so the rest of the NLP
    # preprocessing pipeline has a reliable starting file.
    if not os.path.exists(CLEAN_INPUT_PATH):
        export_clean_sms_dataset()

    df = load_sms_dataset(CLEAN_INPUT_PATH)
    df["clean_message"] = df["message"].apply(clean_text)

    label_map = {"ham": 0, "spam": 1}
    # I map labels to 0 and 1 because machine learning training uses numeric
    # targets rather than text labels.
    df["label"] = df["label"].map(label_map)

    if df["label"].isnull().any():
        raise ValueError("Some labels were not recognised during preprocessing.")

    X = df["clean_message"]
    y = df["label"]

    # I split before vectorizing so the vectorizer learns only from training
    # text, which helps me avoid leaking information from the test set.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # I use TF-IDF here because it is a strong beginner-friendly text feature
    # method that converts messages into weighted numeric vectors.
    vectorizer = TfidfVectorizer(max_features=3000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # I create the processed NLP folder before saving so the pickled outputs
    # have a predictable home inside the project pipeline.
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    outputs_to_save = [
        ("X_train.pkl", X_train_vec),
        ("X_test.pkl", X_test_vec),
        ("y_train.pkl", y_train),
        ("y_test.pkl", y_test),
        ("vectorizer.pkl", vectorizer),
    ]

    for file_name, data_to_save in outputs_to_save:
        output_file = os.path.join(OUTPUT_DIR, file_name)
        with open(output_file, "wb") as file:
            pickle.dump(data_to_save, file)

    print("Preprocessing complete.")
    print(f"Source dataset: {RAW_INPUT_PATH}")
    print("Training samples:", X_train_vec.shape)
    print("Test samples:", X_test_vec.shape)


if __name__ == "__main__":
    main()
