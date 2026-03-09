from pathlib import Path

import pandas as pd


def run_sms_classifier(path=None, test_message=None, verbose=True):
    """Train and evaluate a simple SMS spam model."""
    try:
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.metrics import classification_report
        from sklearn.model_selection import train_test_split
        from sklearn.naive_bayes import MultinomialNB
    except ImportError:
        print(
            "Missing dependency: scikit-learn. "
            "Install it with `pip install scikit-learn`."
        )
        return None

    if path is None:
        project_root = Path(__file__).resolve().parents[2]
        path = project_root / "data" / "SMSSpamCollection"
    else:
        path = Path(path)

    if verbose:
        print("--- Starting NLP Spam Detection ---")

    try:
        my_df = pd.read_csv(path, sep="\t", names=["label", "message"])
    except Exception as exc:
        print(f"Could not load SMS dataset: {exc}")
        return None

    my_df["label_num"] = my_df["label"].map({"ham": 0, "spam": 1})

    X_train, X_test, y_train, y_test = train_test_split(
        my_df["message"],
        my_df["label_num"],
        test_size=0.2,
        random_state=42,
    )

    my_vectorizer = CountVectorizer()
    X_train_transformed = my_vectorizer.fit_transform(X_train)
    X_test_transformed = my_vectorizer.transform(X_test)

    my_ai_model = MultinomialNB()
    my_ai_model.fit(X_train_transformed, y_train)

    predictions = my_ai_model.predict(X_test_transformed)

    if verbose:
        print("\n--- Performance Report ---")
        print(
            classification_report(
                y_test,
                predictions,
                target_names=["Safe (Ham)", "Danger (Spam)"],
            )
        )

    if test_message is None:
        test_message = (
            "URGENT: Your account has been compromised. "
            "Log in at http://bit.ly/fake-bank to secure your funds."
        )

    sample_vec = my_vectorizer.transform([test_message])
    prediction = my_ai_model.predict(sample_vec)[0]
    verdict = "SPAM/PHISHING" if prediction == 1 else "SAFE"

    if verbose:
        print(f"Test message: {test_message}")
        print(f"Verdict: {verdict}")

    return {
        "model": my_ai_model,
        "vectorizer": my_vectorizer,
        "test_message": test_message,
        "test_prediction": int(prediction),
        "test_verdict": verdict,
    }


if __name__ == "__main__":
    run_sms_classifier()
