import json
import os
import pickle
import re
import sys

import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse import hstack
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.preprocess_nlp import RAW_INPUT_PATH
from src.data.preprocess_nlp import export_clean_sms_dataset
from src.data.preprocess_nlp import load_sms_dataset


SAVED_MODELS_DIR = os.path.join(PROJECT_ROOT, "backend", "saved_models")
CLEAN_DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "nlp", "claim_email_ham_spam.tsv")
STAT_FEATURE_COLUMNS = [
    "char_count",
    "word_count",
    "unique_word_ratio",
    "url_count",
    "email_count",
    "has_unsubscribe",
    "phishing_keyword_count",
]


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_keyword_list(dataset: pd.DataFrame) -> list[str]:
    spam_text = " ".join(dataset.loc[dataset["label"] == "spam", "message"].tolist()).lower()
    candidate_keywords = [
        "urgent",
        "immediately",
        "full payout",
        "updated account",
        "updated bank",
        "new bank",
        "transfer the money",
        "send the money",
        "approve this claim today",
        "do not delay",
        "as soon as possible",
        "without delay",
        "full amount",
        "release payment",
        "critical",
    ]
    return [keyword for keyword in candidate_keywords if keyword in spam_text]


def extract_stat_features(text: str, keywords: list[str]) -> dict:
    split_text = text.split()
    lowered_text = text.lower()
    return {
        "char_count": len(text),
        "word_count": len(split_text),
        "unique_word_ratio": len(set(split_text)) / (len(split_text) + 1),
        "url_count": len(re.findall(r"http\S+|www\S+", text)),
        "email_count": len(re.findall(r"\S+@\S+", text)),
        "has_unsubscribe": int("unsubscribe" in lowered_text),
        "phishing_keyword_count": sum(1 for keyword in keywords if keyword in lowered_text),
    }


def prepare_dataset() -> pd.DataFrame:
    export_clean_sms_dataset(RAW_INPUT_PATH, CLEAN_DATASET_PATH)
    dataset = load_sms_dataset(CLEAN_DATASET_PATH)
    dataset["message"] = dataset["message"].map(clean_text)
    dataset = dataset[dataset["label"].isin({"ham", "spam"})].reset_index(drop=True)
    dataset["target"] = dataset["label"].map({"ham": 0, "spam": 1})
    return dataset


def save_pickle(path: str, value) -> None:
    with open(path, "wb") as file:
        pickle.dump(value, file)


def save_json(path: str, value) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(value, file, indent=2)


def main() -> None:
    dataset = prepare_dataset()
    keywords = build_keyword_list(dataset)

    X_train_text, X_test_text, y_train, y_test = train_test_split(
        dataset["message"],
        dataset["target"],
        test_size=0.2,
        random_state=42,
        stratify=dataset["target"],
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=3000)
    X_train_tfidf = vectorizer.fit_transform(X_train_text)
    X_test_tfidf = vectorizer.transform(X_test_text)

    train_stat_frame = pd.DataFrame([extract_stat_features(text, keywords) for text in X_train_text])[STAT_FEATURE_COLUMNS]
    test_stat_frame = pd.DataFrame([extract_stat_features(text, keywords) for text in X_test_text])[STAT_FEATURE_COLUMNS]
    X_train_stat = csr_matrix(train_stat_frame.values)
    X_test_stat = csr_matrix(test_stat_frame.values)

    X_train_combined = hstack([X_train_tfidf, X_train_stat])
    X_test_combined = hstack([X_test_tfidf, X_test_stat])

    selector_k = min(220, X_train_combined.shape[1])
    chi2_selector = SelectKBest(score_func=chi2, k=selector_k)
    X_train_selected = chi2_selector.fit_transform(X_train_combined, y_train)
    X_test_selected = chi2_selector.transform(X_test_combined)

    mnb_model = MultinomialNB(alpha=0.5)
    rf_model = RandomForestClassifier(
        n_estimators=250,
        max_depth=18,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1,
    )

    mnb_model.fit(X_train_selected, y_train)
    rf_model.fit(X_train_selected, y_train)

    mnb_predictions = mnb_model.predict(X_test_selected)
    rf_predictions = rf_model.predict(X_test_selected)
    mnb_probabilities = mnb_model.predict_proba(X_test_selected)[:, 1]
    rf_probabilities = rf_model.predict_proba(X_test_selected)[:, 1]

    metrics = {
        "dataset_path": os.path.relpath(RAW_INPUT_PATH, PROJECT_ROOT),
        "rows": int(len(dataset)),
        "train_rows": int(len(X_train_text)),
        "test_rows": int(len(X_test_text)),
        "selected_features": int(X_train_selected.shape[1]),
        "models": {
            "MultinomialNB": {
                "accuracy": round(float(accuracy_score(y_test, mnb_predictions)), 4),
                "precision": round(float(precision_score(y_test, mnb_predictions)), 4),
                "recall": round(float(recall_score(y_test, mnb_predictions)), 4),
                "f1": round(float(f1_score(y_test, mnb_predictions)), 4),
                "roc_auc": round(float(roc_auc_score(y_test, mnb_probabilities)), 4),
            },
            "RandomForest": {
                "accuracy": round(float(accuracy_score(y_test, rf_predictions)), 4),
                "precision": round(float(precision_score(y_test, rf_predictions)), 4),
                "recall": round(float(recall_score(y_test, rf_predictions)), 4),
                "f1": round(float(f1_score(y_test, rf_predictions)), 4),
                "roc_auc": round(float(roc_auc_score(y_test, rf_probabilities)), 4),
            },
        },
    }

    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    save_pickle(os.path.join(SAVED_MODELS_DIR, "mnb_model.pkl"), mnb_model)
    save_pickle(os.path.join(SAVED_MODELS_DIR, "rf_model.pkl"), rf_model)
    save_pickle(os.path.join(SAVED_MODELS_DIR, "tfidf_vectorizer.pkl"), vectorizer)
    save_pickle(os.path.join(SAVED_MODELS_DIR, "chi2_selector.pkl"), chi2_selector)
    save_json(os.path.join(SAVED_MODELS_DIR, "phishing_keywords.json"), keywords)
    save_json(os.path.join(SAVED_MODELS_DIR, "stat_feature_cols.json"), STAT_FEATURE_COLUMNS)
    save_json(os.path.join(SAVED_MODELS_DIR, "nlp_metrics.json"), metrics)

    print("Insurance claim-email NLP models saved.")
    print(f"Dataset: {metrics['dataset_path']}")
    print(f"Rows: {metrics['rows']} | Train: {metrics['train_rows']} | Test: {metrics['test_rows']}")
    print(f"Naive Bayes F1: {metrics['models']['MultinomialNB']['f1']}")
    print(f"Random Forest F1: {metrics['models']['RandomForest']['f1']}")


if __name__ == "__main__":
    main()
