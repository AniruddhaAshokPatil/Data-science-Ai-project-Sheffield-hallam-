# Anomaly Model Summary

I use this note to explain how the anomaly model supports the wider fraud
project and what evidence now exists in the repository.

## Purpose

The anomaly model gives the project a second opinion beyond the supervised
transaction score. I use it to learn what legitimate card behavior looks like,
then flag records that drift away from that baseline even when a rule-based or
supervised model might stay uncertain.

## Training Path

- script: `src/train/train_anomaly_model.py`
- saved model: `src/train/artifacts/isolation_forest.joblib`
- saved metadata: `src/train/artifacts/isolation_forest.metadata.pkl`
- default dataset: `data/processed/transactions/clean_validation.csv`

## What I Fixed

- I moved the anomaly artifact path into the shared model-path module so
  training, readiness checks, and API inference all agree on one location.
- I save feature names and calibration values with the model metadata so I can
  convert the raw Isolation Forest output into a project-friendly risk score.
- I added evaluation that compares anomaly alerts against a supervised baseline
  so I can see when anomaly detection catches extra frauds and when it adds
  extra false positives.

## Why This Supports the Project

- It gives the monitoring dashboard a behavior-based signal instead of relying
  only on direct classification.
- It makes the fraud story more realistic, because unusual behavior often
  matters even when labels are sparse or patterns shift.
- It helps justify the "multimodal" design by showing how a second model can
  complement the main transaction score.
