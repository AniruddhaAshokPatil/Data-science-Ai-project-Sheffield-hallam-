# Project Traceability

Audit date: 2026-04-09

I wrote this file so I could explain, in a straightforward way, what is actually inside this repository right now.
I am using the files that are really tracked in `main` as my reference point, because I want this explanation to match the project I truly have in front of me, not an older plan or a bigger version that was never fully tracked here.

## What The Project Looks Like Right Now

Right now, when I look at this repository, I can see that it mainly includes:

- A Streamlit application entrypoint in `App_Frontend.py`
- A local project data area in `data/`
- Data-preparation scripts in `src/data/`
- Model-training notebooks in `backend/`
- Saved NLP, receipt-CV, and ID-card artifacts in `backend/saved_models/` and `backend/receipts_models/`
- Supporting documentation in `docs/`

At the same time, I also need to be honest about what is not here. I do not currently see the full tracked FastAPI source, React source, or end-to-end test source, even though some older GitHub issues describe that kind of setup.

## How I Read The Main Folders

| Path | Role in current repo | Notes |
| --- | --- | --- |
| `App_Frontend.py` | Main user-facing application | Streamlit interface for NLP, receipt, and ID-card analysis |
| `data/` | Main project data area | Raw and processed project datasets |
| `src/data/` | Data preparation layer | Collection, cleaning, preprocessing, encoding, and feature engineering scripts |
| `backend/` | Experimentation and training | Notebooks and saved model artifacts |
| `backend/saved_models/` | NLP and ID-card model artifacts | Includes TF-IDF, classifiers, One-Class SVM, scaler, and config |
| `backend/receipts_models/` | Receipt-CV model artifacts | Includes receipt model and metrics/config files |
| `Datasets/` | Older extra dataset storage | Some source data still exists here, but the project now also exposes local working copies through `data/` |
| `docs/` | Documentation layer | Traceability and issue alignment documents |
| `readme.md` | Project entrypoint documentation | Setup, usage, and high-level system overview |

## How I Match This To The Issues

If I want to understand how the GitHub issues line up with the files that are actually present, I use:

- `docs/ISSUE_ALIGNMENT.md`

In that document, I explain:

- Which issues match the tracked files
- Which issues are only partially evidenced
- Which issues describe planned architecture that is not present in `main`

## Where Each Part Comes From

In this section, I show which notebooks and saved files support each part of the project. I am doing this because I want it to be easy to trace where each visible feature in the app is actually coming from.

### NLP

- Training notebook: `backend/Phisihing_Model_NLP.ipynb`
- Local data paths:
  - `data/raw/nlp/SMSSpamCollection.csv`
  - `data/raw/nlp/sms_spam.csv`
  - `data/raw/nlp/enron_spam_data.csv`
- Saved artifacts:
  - `backend/saved_models/mnb_model.pkl`
  - `backend/saved_models/rf_model.pkl`
  - `backend/saved_models/tfidf_vectorizer.pkl`
  - `backend/saved_models/chi2_selector.pkl`
  - `backend/saved_models/phishing_keywords.json`
  - `backend/saved_models/stat_feature_cols.json`

### Receipt CV

- Training notebook: `backend/Fraud_Receipt_Detection_CV.ipynb`
- Local data path:
  - `data/raw/cv/Receipt_Fraud_Dataset/`
- Saved artifacts:
  - `backend/receipts_models/mobilenet_receipt_fraud.keras`
  - `backend/receipts_models/cv_config.json`
  - `backend/receipts_models/cv_metrics.json`

### ID Card CV / Anomaly

- Training notebook: `backend/Midv2019_ID_Card_Fraud_Detection.ipynb`
- Local data path:
  - `data/raw/cv/midv500_data/`
- Saved artifacts:
  - `backend/saved_models/mobilenet_final.h5`
  - `backend/saved_models/ocsvm.pkl`
  - `backend/saved_models/feature_scaler.pkl`
  - `backend/saved_models/label_encoder.pkl`
  - `backend/saved_models/model_config.json`

## What I Still Cannot Fully Trace

These are the main things I can see mentioned in older notes or GitHub issues, but I still cannot fully trace them in the repository as it exists today:

- React source frontend
- FastAPI source backend
- WebSocket source implementation
- Tracked integration-test source
- Some project-management documents referenced by closed issues
- Some model files mentioned in older docs and issue descriptions

## My Ground Rule

My ground rule is simple: if the issues, the documentation, and the files disagree with each other, I trust the tracked files in `main` first. After that, I update the notes so the explanation matches the codebase, instead of forcing the codebase to match an outdated description.
