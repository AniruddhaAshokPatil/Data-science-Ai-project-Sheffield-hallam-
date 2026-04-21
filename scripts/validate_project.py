import importlib
import importlib.metadata
import importlib.util
import json
import os


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
RECEIPT_MODELS_DIR = os.path.join(BACKEND_DIR, "receipts_models")
SAVED_MODELS_DIR = os.path.join(BACKEND_DIR, "saved_models")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)


def print_title(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def check_file_exists(file_path):
    exists = os.path.exists(file_path)
    status = "OK" if exists else "MISSING"
    print(f"[{status}] {file_path}")
    return exists


def check_import(module_name, display_name=None):
    label = display_name or module_name
    try:
        if importlib.util.find_spec(module_name) is None:
            raise ModuleNotFoundError(module_name)

        try:
            version = importlib.metadata.version(module_name)
        except importlib.metadata.PackageNotFoundError:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", "unknown")

        print(f"[OK] {label} is available ({version})")
        return True
    except Exception as error:
        print(f"[ERROR] {label} is not available: {error}")
        return False


def check_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        print(f"[OK] JSON file loaded: {file_path}")
        return True, data
    except Exception as error:
        print(f"[ERROR] JSON file could not be read: {file_path}")
        print(f"        {error}")
        return False, None


def check_core_files():
    print_title("1. Checking Submission Files")
    files_to_check = [
        os.path.join(PROJECT_ROOT, "readme.md"),
        os.path.join(PROJECT_ROOT, "run_all.sh"),
        os.path.join(PROJECT_ROOT, "docs", "PROJECT_TRACEABILITY.md"),
        os.path.join(PROJECT_ROOT, "docs", "ISSUE_ALIGNMENT.md"),
        os.path.join(PROJECT_ROOT, "docs", "INSURANCE_CLAIM_SAMPLES.md"),
        os.path.join(PROJECT_ROOT, "src", "api", "main.py"),
        os.path.join(PROJECT_ROOT, "src", "frontend", "package.json"),
        os.path.join(PROJECT_ROOT, "tests", "test_api_insurance.py"),
    ]
    return all(check_file_exists(path) for path in files_to_check)


def check_environment():
    print_title("2. Checking Python Packages")
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pandas", "pandas"),
        ("httpx", "httpx"),
        ("pytest", "pytest"),
        ("multipart", "python-multipart"),
    ]
    optional_packages = [
        ("tensorflow", "TensorFlow"),
        ("keras", "Keras"),
        ("spacy", "spaCy"),
    ]

    all_ok = True
    for module_name, display_name in required_packages:
        if not check_import(module_name, display_name):
            all_ok = False

    print("\nOptional model-development packages:")
    for module_name, display_name in optional_packages:
        if not check_import(module_name, display_name):
            print(f"[WARN] {display_name} is only needed for training or rebuilding supporting model artifacts.")

    return all_ok


def check_model_files():
    print_title("3. Checking Saved Model Files")
    model_files = [
        os.path.join(RECEIPT_MODELS_DIR, "mobilenet_receipt_fraud.keras"),
        os.path.join(RECEIPT_MODELS_DIR, "resnet50_receipt_fraud.keras"),
        os.path.join(RECEIPT_MODELS_DIR, "cv_config.json"),
        os.path.join(RECEIPT_MODELS_DIR, "cv_metrics.json"),
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
    return all(check_file_exists(path) for path in model_files)


def check_local_data_files():
    print_title("4. Checking Local Data Files")
    data_files = [
        os.path.join(DATA_DIR, "raw", "nlp", "claim_email_ham_spam.csv"),
        os.path.join(DATA_DIR, "raw", "insurance_claims", "claim_history_detailed.csv"),
        os.path.join(DATA_DIR, "raw", "insurance_claims", "claim_history_detailed_dictionary.md"),
    ]
    return all(check_file_exists(path) for path in data_files)


def check_frontend_files():
    print_title("5. Checking Frontend Files")
    files_to_check = [
        os.path.join(PROJECT_ROOT, "src", "frontend", "index.html"),
        os.path.join(PROJECT_ROOT, "src", "frontend", "vite.config.js"),
        os.path.join(PROJECT_ROOT, "src", "frontend", "src", "App.jsx"),
        os.path.join(PROJECT_ROOT, "src", "frontend", "src", "data", "mockData.js"),
        os.path.join(PROJECT_ROOT, "src", "frontend", "src", "main.jsx"),
        os.path.join(PROJECT_ROOT, "src", "frontend", "src", "styles.css"),
    ]
    return all(check_file_exists(path) for path in files_to_check)


def check_configs():
    print_title("6. Checking Config Files")
    all_ok = True

    receipt_config_ok, receipt_config = check_json_file(os.path.join(RECEIPT_MODELS_DIR, "cv_config.json"))
    receipt_metrics_ok, receipt_metrics = check_json_file(os.path.join(RECEIPT_MODELS_DIR, "cv_metrics.json"))
    id_config_ok, id_config = check_json_file(os.path.join(SAVED_MODELS_DIR, "model_config.json"))

    if not receipt_config_ok or not receipt_metrics_ok or not id_config_ok:
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

    id_models = id_config.get("models", {})
    required_id_keys = ["mobilenet", "resnet", "ocsvm", "scaler", "encoder"]
    missing_keys = [key for key in required_id_keys if key not in id_models]
    if missing_keys:
        print(f"[ERROR] ID config is missing these model entries: {missing_keys}")
        all_ok = False
    else:
        print("[OK] ID config includes all expected model entries.")

    return all_ok


def print_final_summary(results):
    print_title("7. Final Summary")
    failed_sections = [section_name for section_name, section_result in results.items() if not section_result]
    if failed_sections:
        print("I found a few things that still need attention.")
        print("Sections with problems:")
        for section_name in failed_sections:
            print(f"- {section_name}")
        return 1

    print("Everything I checked looks good.")
    print("The cleaned repository layout, main apps, and tracked model files all line up.")
    return 0


def main():
    results = {
        "core_files": check_core_files(),
        "environment": check_environment(),
        "model_files": check_model_files(),
        "local_data": check_local_data_files(),
        "frontend_files": check_frontend_files(),
        "configs": check_configs(),
    }
    raise SystemExit(print_final_summary(results))


if __name__ == "__main__":
    main()
