# NLP Preprocessing Summary

I am keeping this note because GitHub issue `#3` is titled like a CV task, but
its body actually asks for the SMS spam preprocessing deliverable.

## Expected Outputs Already Present

- `data/processed/nlp/X_train.pkl`
- `data/processed/nlp/X_test.pkl`
- `data/processed/nlp/y_train.pkl`
- `data/processed/nlp/y_test.pkl`
- `data/processed/nlp/vectorizer.pkl`

## Pipeline Evidence

- preprocessing script: `src/data/preprocess_nlp.py`
- raw dataset path: `data/raw/nlp/SMSSpamCollection.csv`
- cleaned corpus path: `data/SMSSpamCollection`

## How This Supports the Project

- I split train and test data before fitting TF-IDF so the project avoids data leakage.
- I cap TF-IDF vocabulary size to keep inference practical for the API.
- I save the vectorized outputs so later training and evaluation steps can reuse
  the same prepared data without redoing the whole preprocessing stage.
