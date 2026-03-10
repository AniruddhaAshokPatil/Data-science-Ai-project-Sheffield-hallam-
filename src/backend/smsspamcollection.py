import pandas as pd
from pathlib import Path

# Simple imports (much easier for beginners)
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.naive_bayes import MultinomialNB
import joblib


def run_sms_classifier(
    path=None,
    test_message=None,
    verbose=True,
    test_size=0.2,
    random_state=42,
    save_dir=None,
):
    """Train and test a simple SMS spam detection model."""

    # ------------------------
    #  Load Dataset
    # ------------------------
    if path is None:
        project_root = Path(__file__).resolve().parents[2]
        path = project_root / "data" / "SMSSpamCollection"
    else:
        path = Path(path)

    if not path.exists():
        print(f"Error: dataset not found at {path}")
        return None

    try:
        df = pd.read_csv(
            path,
            sep="\t",
            names=["label", "message"],
            encoding="utf-8",
            on_bad_lines="skip"
        )
    except Exception as e:
        print("Could not read dataset:", e)
        return None

    # ------------------------
    #  Clean Dataset
    # ------------------------
    df["label_num"] = df["label"].map({"ham": 0, "spam": 1})
    df = df.dropna(subset=["label_num"])

    # ------------------------
    #  Train Test Split
    # ------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        df["message"],
        df["label_num"],
        test_size=test_size,
        random_state=random_state,
        stratify=df["label_num"]
    )

    # ------------------------
    #  Vectorizer + Naive Bayes
    # ------------------------
    vectorizer = CountVectorizer()
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = MultinomialNB()
    model.fit(X_train_vec, y_train)

    # ------------------------
    #  Evaluation
    # ------------------------
    predictions = model.predict(X_test_vec)

    if verbose:
        print("\n--- Model Report ---")
        print(classification_report(y_test, predictions))
        print("Confusion Matrix:")
        print(confusion_matrix(y_test, predictions))

    # ------------------------
    #  Test Message
    # ------------------------
    if test_message is None:
        test_message = "URGENT: Your bank account is locked. Click http://fake.com"

    sample_vec = vectorizer.transform([test_message])
    pred = model.predict(sample_vec)[0]

    verdict = "SPAM" if pred == 1 else "SAFE"

    if verbose:
        print("\nTest Message:", test_message)
        print("Prediction:", verdict)

    # ------------------------
    #  Save Model
    # ------------------------
    if save_dir:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, save_dir / "sms_model.joblib")
        joblib.dump(vectorizer, save_dir / "sms_vectorizer.joblib")

    return {
        "verdict": verdict,
        "model": model,
        "vectorizer": vectorizer
    }


if __name__ == "__main__":
    run_sms_classifier()
