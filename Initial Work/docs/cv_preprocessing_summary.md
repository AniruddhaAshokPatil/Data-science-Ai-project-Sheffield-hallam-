# CV Preprocessing Summary

I use this note to summarize the current preprocessing state of the document CV dataset.

## Inputs

- Raw images from `data/raw/cv/midv500_data/midv500`

## Outputs

- Processed image folders under `data/processed/cv/train/` and `data/processed/cv/test/`
- Labels file: `data/processed/cv/labels.csv`

## Verified Current Output

- Total labeled rows: `400`
- Train rows: `320`
- Test rows: `80`

## Processing Logic

- resize images to a model-friendly size
- create original samples with label `0`
- create distorted samples with label `1`
- assign train/test split

## Repository Evidence

- preprocessing script: `src/data/preprocess_cv_data.py`
- dataset loader: `src/data/dataset.py`
- training script: `src/train/train_cv_model.py`
