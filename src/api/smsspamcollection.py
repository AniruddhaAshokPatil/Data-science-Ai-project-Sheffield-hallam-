import pandas as pd
from pathlib import Path

# I keep these imports simple because this helper is meant to be readable as a small end-to-end NLP example.
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
import joblib

from src.data.preprocess_nlp import load_sms_dataset


def run_sms_classifier(
    path=None,
    test_message=None,
    verbose=True,
    test_size=0.2,
    random_state=42,
    save_dir=None,
):
    """Train and test a simple SMS spam detection model."""

    # I build the default path here so this file can run on its own and still find the project dataset.
    if path is None:
        project_root = Path(__file__).resolve().parents[2]
        path = project_root / "data" / "raw" / "nlp" / "sms_spam.csv"
    else:
        path = Path(path)

    if not path.exists():
        print(f"Error: dataset not found at {path}")
        return None

    try:
        dataframe = load_sms_dataset(path)
    except Exception as e:
        print("Could not read dataset:", e)
        return None

    # I convert the text labels into numbers because the model can train only on numeric targets.
    dataframe["label_num"] = dataframe["label"].map({"ham": 0, "spam": 1})
    dataframe = dataframe.dropna(subset=["label_num"])

    # I split the messages here so I can test the model on messages it did not train on.
    X_train, X_test, y_train, y_test = train_test_split(
        dataframe["message"],
        dataframe["label_num"],
        test_size=test_size,
        random_state=random_state,
        stratify=dataframe["label_num"],
    )

    # I use CountVectorizer because raw words must be turned into numbers before Naive Bayes can learn from them.
    vectorizer = CountVectorizer()
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = MultinomialNB()
    model.fit(X_train_vec, y_train)

    # I predict on the test split so I can see whether the model generalizes beyond the training rows.
    predictions = model.predict(X_test_vec)

    if verbose:
        print("\n--- Model Report ---")
        print(classification_report(y_test, predictions))
        print("Confusion Matrix:")
        print(confusion_matrix(y_test, predictions))

    # I keep one sample message here so this file can prove the NLP branch works by itself.
    if test_message is None:
        test_message = "URGENT: Your bank account is locked. Click http://fake.com"

    sample_vec = vectorizer.transform([test_message])
    pred = model.predict(sample_vec)[0]

    verdict = "SPAM" if pred == 1 else "SAFE"

    if verbose:
        print("\nTest Message:", test_message)
        print("Prediction:", verdict)

    # I save the model together with the vectorizer because later predictions need the same word mapping.
    if save_dir:
        save_folder = Path(save_dir)
        save_folder.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, save_folder / "sms_model.joblib")
        joblib.dump(vectorizer, save_folder / "sms_vectorizer.joblib")

    result = {
        "verdict": verdict,
        "model": model,
        "vectorizer": vectorizer,
    }
    return result


if __name__ == "__main__":
    run_sms_classifier()
