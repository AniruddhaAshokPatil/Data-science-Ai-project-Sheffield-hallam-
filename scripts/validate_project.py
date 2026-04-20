import json
import os


# I keep the project paths at the top so it is easy to see what this checker uses.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
RECEIPT_MODELS_DIR = os.path.join(BACKEND_DIR, "receipts_models")
SAVED_MODELS_DIR = os.path.join(BACKEND_DIR, "saved_models")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# I set these environment values early so the checker output stays cleaner.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)


def print_title(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def check_file_exists(file_path):
    # I use one small helper so every file check prints the same kind of message.
    exists = os.path.exists(file_path)
    status = "OK" if exists else "MISSING"
    print(f"[{status}] {file_path}")
    return exists


def check_import(module_name, display_name=None):
    # I test imports here because a project can look complete on disk
    # but still fail if the environment is missing packages.
    import importlib

    label = display_name or module_name

    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "unknown")
        print(f"[OK] {label} imported successfully ({version})")
        return True
    except Exception as error:
        print(f"[ERROR] {label} could not be imported: {error}")
        return False


def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def check_json_file(file_path):
    try:
        data = load_json_file(file_path)
        print(f"[OK] JSON file loaded: {file_path}")
        return True, data
    except Exception as error:
        print(f"[ERROR] JSON file could not be read: {file_path}")
        print(f"        {error}")
        return False, None


def check_core_files():
    print_title("1. Checking Main Project Files")

    files_to_check = [
        os.path.join(PROJECT_ROOT, "App_Frontend.py"),
        os.path.join(PROJECT_ROOT, "readme.md"),
        os.path.join(PROJECT_ROOT, "requirements.txt"),
        os.path.join(PROJECT_ROOT, "docs", "PROJECT_TRACEABILITY.md"),
        os.path.join(PROJECT_ROOT, "docs", "ISSUE_ALIGNMENT.md"),
        os.path.join(PROJECT_ROOT, "scripts", "rebuild_missing_models.py"),
    ]

    all_ok = True
    for file_path in files_to_check:
        if not check_file_exists(file_path):
            all_ok = False

    return all_ok


def check_environment():
    print_title("2. Checking Python Packages")

    packages_to_check = [
        ("streamlit", "Streamlit"),
        ("tensorflow", "TensorFlow"),
        ("keras", "Keras"),
        ("numpy", "NumPy"),
        ("pandas", "pandas"),
        ("sklearn", "scikit-learn"),
        ("scipy", "SciPy"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("PIL", "Pillow"),
        ("spacy", "spaCy"),
        ("shap", "SHAP"),
        ("cv2", "OpenCV"),
    ]

    all_ok = True
    for module_name, display_name in packages_to_check:
        if not check_import(module_name, display_name):
            all_ok = False

    return all_ok


def check_model_files():
    print_title("3. Checking Saved Model Files")

    model_files = [
        os.path.join(RECEIPT_MODELS_DIR, "mobilenet_receipt_fraud.keras"),
        os.path.join(RECEIPT_MODELS_DIR, "resnet50_receipt_fraud.keras"),
        os.path.join(RECEIPT_MODELS_DIR, "cv_config.json"),
        os.path.join(RECEIPT_MODELS_DIR, "cv_metrics.json"),
        os.path.join(SAVED_MODELS_DIR, "transaction_fraud_model.pkl"),
        os.path.join(SAVED_MODELS_DIR, "transaction_metrics.json"),
        os.path.join(SAVED_MODELS_DIR, "transaction_model_config.json"),
        os.path.join(SAVED_MODELS_DIR, "card_transaction_fraud_model.pkl"),
        os.path.join(SAVED_MODELS_DIR, "card_transaction_metrics.json"),
        os.path.join(SAVED_MODELS_DIR, "card_transaction_model_config.json"),
        os.path.join(SAVED_MODELS_DIR, "mnb_model.pkl"),
        os.path.join(SAVED_MODELS_DIR, "rf_model.pkl"),
        os.path.join(SAVED_MODELS_DIR, "tfidf_vectorizer.pkl"),
        os.path.join(SAVED_MODELS_DIR, "chi2_selector.pkl"),
        os.path.join(SAVED_MODELS_DIR, "phishing_keywords.json"),
        os.path.join(SAVED_MODELS_DIR, "stat_feature_cols.json"),
        os.path.join(SAVED_MODELS_DIR, "mobilenet_final.h5"),
        os.path.join(SAVED_MODELS_DIR, "resnet_final.h5"),
        os.path.join(SAVED_MODELS_DIR, "ocsvm.pkl"),
        os.path.join(SAVED_MODELS_DIR, "feature_scaler.pkl"),
        os.path.join(SAVED_MODELS_DIR, "label_encoder.pkl"),
        os.path.join(SAVED_MODELS_DIR, "model_config.json"),
    ]

    all_ok = True
    for file_path in model_files:
        if not check_file_exists(file_path):
            all_ok = False

    return all_ok


def check_local_data_files():
    print_title("3. Checking Local Data Folder")

    data_files = [
        os.path.join(DATA_DIR, "raw", "nlp", "SMSSpamCollection.csv"),
        os.path.join(DATA_DIR, "raw", "nlp", "sms_spam.csv"),
        os.path.join(DATA_DIR, "raw", "transactions", "financial_fraud_detection_dataset.csv"),
        os.path.join(DATA_DIR, "raw", "transactions", "card_transdata.csv"),
        os.path.join(DATA_DIR, "raw", "cv", "Receipt_Fraud_Dataset"),
    ]

    all_ok = True
    for file_path in data_files:
        if not check_file_exists(file_path):
            all_ok = False

    return all_ok


def check_model_configs():
    print_title("4. Checking Model Config Files")

    all_ok = True

    receipt_config_path = os.path.join(RECEIPT_MODELS_DIR, "cv_config.json")
    receipt_metrics_path = os.path.join(RECEIPT_MODELS_DIR, "cv_metrics.json")
    transaction_config_path = os.path.join(SAVED_MODELS_DIR, "transaction_model_config.json")
    card_transaction_config_path = os.path.join(SAVED_MODELS_DIR, "card_transaction_model_config.json")
    id_config_path = os.path.join(SAVED_MODELS_DIR, "model_config.json")

    receipt_config_ok, receipt_config = check_json_file(receipt_config_path)
    receipt_metrics_ok, receipt_metrics = check_json_file(receipt_metrics_path)
    transaction_config_ok, transaction_config = check_json_file(transaction_config_path)
    card_transaction_config_ok, card_transaction_config = check_json_file(card_transaction_config_path)
    id_config_ok, id_config = check_json_file(id_config_path)

    if not receipt_config_ok or not receipt_metrics_ok or not transaction_config_ok or not card_transaction_config_ok or not id_config_ok:
        return False

    if "mobilenet_model" not in receipt_config or "resnet_model" not in receipt_config:
        print("[ERROR] Receipt config is missing one or more model names.")
        all_ok = False
    else:
        print("[OK] Receipt config includes both receipt model names.")

    if "MobileNetV2" not in receipt_metrics or "ResNet50" not in receipt_metrics:
        print("[ERROR] Receipt metrics do not include both receipt models.")
        all_ok = False
    else:
        print("[OK] Receipt metrics include both receipt models.")

    if transaction_config.get("dataset_name") == "financial_fraud_detection_dataset.csv":
        print("[OK] Main transaction config is linked to the financial fraud dataset.")
    else:
        print("[ERROR] Main transaction config is not linked to the expected dataset.")
        all_ok = False

    if card_transaction_config.get("dataset_name") == "card_transdata.csv":
        print("[OK] Card transaction config is linked to the card transaction dataset.")
    else:
        print("[ERROR] Card transaction config is not linked to the expected dataset.")
        all_ok = False

    id_models = id_config.get("models", {})
    needed_id_keys = ["mobilenet", "resnet", "ocsvm", "scaler", "encoder"]

    missing_keys = []
    for key in needed_id_keys:
        if key not in id_models:
            missing_keys.append(key)

    if missing_keys:
        print(f"[ERROR] ID config is missing these model entries: {missing_keys}")
        all_ok = False
    else:
        print("[OK] ID config includes all expected model entries.")

    return all_ok


def print_final_summary(results):
    print_title("5. Final Summary")

    failed_sections = []

    for section_name, section_result in results.items():
        if not section_result:
            failed_sections.append(section_name)

    if failed_sections:
        print("I found a few things that still need attention.")
        print("Sections with problems:")
        for section_name in failed_sections:
            print(f"- {section_name}")
        return 1

    print("Everything I checked looks good.")
    print("The project files, environment, and saved model files all line up.")
    return 0


def main():
    results = {
        "main_files": check_core_files(),
        "environment": check_environment(),
        "local_data": check_local_data_files(),
        "model_files": check_model_files(),
        "model_configs": check_model_configs(),
    }

    exit_code = print_final_summary(results)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
