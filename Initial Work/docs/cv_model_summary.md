# CV Model Summary

I use this note to show how the document-forgery model supports the project and
what proof exists for the training path.

## Dataset and Preprocessing Evidence

- raw dataset summary: `docs/cv_dataset_collection.md`
- preprocessing summary: `docs/cv_preprocessing_summary.md`
- processed labels: `data/processed/cv/labels.csv`
- saved model artifact: `src/train/artifacts/simple_cnn.pth`

## Training Path

- dataset loader: `src/data/dataset.py`
- preprocessing pipeline: `src/data/preprocess_cv_data.py`
- training script: `src/train/train_cv_model.py`
- evaluation script: `src/train/evaluate_cv_model.py`

## What I Fixed

- I aligned the training script with the shared `SimpleCNN` architecture so the
  API and the training code now expect the same model shape.
- I fixed the dataset loader so it can accept either a CSV path or a prepared
  DataFrame, which makes training and evaluation easier to reuse.
- I expanded the evaluator so it can report confusion-matrix style results, not
  just a single accuracy number.

## Why This Supports the Project

- It gives the fraud platform a document-focused signal that is separate from
  transaction behavior and text analysis.
- It demonstrates how forged or degraded ID images can be modeled as part of
  one shared fraud triage workflow.
- It makes the dashboard story stronger because the system can describe model
  readiness for CV as well as transaction and NLP components.
