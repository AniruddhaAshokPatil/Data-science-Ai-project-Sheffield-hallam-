# CV Dataset Collection Summary

I use this note to document the collected document-image dataset that supports
the CV fraud component of the project.

## Dataset

- Source family: MIDV-500 style document dataset
- Local path: `data/raw/cv/midv500_data/midv500`
- Verified local file count: approximately `15,050` image files

## Why It Matters

- I need a document dataset so the project can simulate forged vs genuine
  document scenarios for the CV fraud path.
- The dataset supports later preprocessing, synthetic distortions, and CV model training.

## Repository Evidence

- Collection helper: `src/data/collect_cv_data.py`
- Raw dataset tree present under `data/raw/cv/midv500_data/midv500`
- Processed outputs already exist under `data/processed/cv/`

## Current Limitation

- The project uses synthetic distortions to simulate fraud, so this is still a
  proxy for real-world document forgery rather than a perfect ground-truth dataset.
