import os
import sys

# I add the project root to sys.path here so this small helper script can
# import the shared preprocessing module even when I run it directly.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.preprocess_nlp import CLEAN_INPUT_PATH, RAW_INPUT_PATH, export_clean_sms_dataset


def main():
    # I call the shared export function here because I want one simple command
    # that writes the cleaned NLP dataset into the format used by the project.
    df = export_clean_sms_dataset(RAW_INPUT_PATH, CLEAN_INPUT_PATH)
    print(f"I wrote the clean NLP dataset to: {CLEAN_INPUT_PATH}")
    print(f"Source dataset: {RAW_INPUT_PATH}")
    print(f"Rows written: {len(df)}")


if __name__ == "__main__":
    main()
