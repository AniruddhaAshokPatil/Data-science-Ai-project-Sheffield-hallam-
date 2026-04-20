# GitHub Issue Alignment

Audit date: 2026-04-09

I wrote this file as a reality check between the GitHub issues and the files that are actually present in the repository.
I am basing this on what is currently tracked in `main`, because I want to explain the project from the evidence that is really there, not from older plans, assumptions, or architecture that never fully showed up in the repo.

## Closed Issues I Checked

In this section, I am looking at the issues that were already closed and asking one simple question: can I still see enough evidence for that work in the current repository?

| Issue | Title | Status vs current repo | Matching files |
| --- | --- | --- | --- |
| #1 | Preprocess NLP Dataset (Cleaning & Tokenisation) | Implemented in current tree | `src/data/clean_sms_dataset.py`, `src/data/preprocess_nlp.py` |
| #2 | Collect Phishing / Fraud Text NLP Dataset | Implemented in current tree | `data/raw/nlp/SMSSpamCollection.csv`, `data/raw/nlp/sms_spam.csv`, `data/raw/nlp/enron_spam_data.csv` |
| #3 | Preprocess CV Dataset (Resize/Normalise/Split) | Partially aligned; issue body appears to describe NLP, but CV preprocessing code exists | `src/data/preprocess_cv_data.py` |
| #4 | Collect Document/ID Fraud CV Dataset | Partially aligned; receipt dataset is present in the local data folder, but MIDV raw image files are still not fully tracked here | `data/raw/cv/Receipt_Fraud_Dataset/`, `data/raw/cv/midv500_data/`, `backend/Midv2019_ID_Card_Fraud_Detection.ipynb` |
| #5 | Create Time-Based Train or Test Split | Implemented in current tree | `src/data/split_transactions.py` |
| #6 | Encode Categorical Features | Implemented in current tree | `src/data/encode_transactions.py` |
| #7 | Feature Engineering: Behaviour & Velocity | Implemented in current tree | `src/data/feature_engineering.py` |
| #8 | Clean Data: Missing Values & Sparse Features | Implemented in current tree | `src/data/clean_transactions.py`, `src/data/inspect_transactions.py` |
| #9 | Merge Transaction & Identity Tables | Evidence is incomplete in current tree; only a compiled artifact remains | `src/data/__pycache__/merge_transaction_identity.cpython-311.pyc` |
| #10 | Download the Financial Transactions Fraud Detection dataset | Not traceable from tracked data files in current tree | No tracked dataset file found |
| #11 | Create Risk Register & Risk Heat Map | Partially aligned | `Initial Work/risk_visualization.png`, `.git/PROJECT_TRACEABILITY.md` |
| #12 | Create RACI Matrix | Not traceable from tracked files in current tree | No tracked RACI document found |
| #13 | Create Gantt Chart for Project | Not traceable from tracked files in current tree | No tracked Gantt document found |
| #14 | Create Project Charter | Not traceable from tracked files in current tree | No tracked charter document found |
| #15 | Train Baseline Fraud Classifier (Tabular) | Partially aligned; source training code is not tracked, but data pipeline scripts exist | `src/data/*.py` |
| #16 | Tune Fraud Classifier & Handle Imbalance | Not directly traceable from tracked files in current tree | No tracked tuning notebook or script found |
| #17 | Train Anomaly Detection Model | Mismatch with current artifacts; repo contains ID-card anomaly artifacts, not transaction anomaly evidence | `backend/saved_models/ocsvm.pkl`, `backend/saved_models/feature_scaler.pkl`, `backend/saved_models/model_config.json` |
| #18 | Train Simple CV Model for Document Forgery | Implemented for receipt CV in current tree | `backend/Fraud_Receipt_Detection_CV.ipynb`, `backend/receipts_models/` |
| #19 | Train Simple NLP Phishing Classifier | Implemented in current tree | `backend/Phisihing_Model_NLP.ipynb`, `backend/saved_models/mnb_model.pkl`, `backend/saved_models/rf_model.pkl`, `backend/saved_models/tfidf_vectorizer.pkl` |
| #20 | Set Up FastAPI Backend Skeleton | Evidence is incomplete in current tree; only compiled API artifacts remain | `src/api/__pycache__/main.cpython-311.pyc`, `src/api/services/__pycache__/tabular.cpython-311.pyc` |
| #21 | Add Prediction Endpoints for Tabular, CV, NLP Models | Evidence is incomplete in current tree; only compiled API/router artifacts remain | `src/api/routers/__pycache__/cv.cpython-311.pyc`, `src/api/routers/__pycache__/nlp.cpython-311.pyc`, `src/api/services/__pycache__/cv.cpython-311.pyc`, `src/api/services/__pycache__/nlp.cpython-311.pyc`, `src/api/services/__pycache__/tabular.cpython-311.pyc` |
| #22 | Implement WebSocket Alert Stream in Backend | Evidence is incomplete in current tree; only compiled WebSocket artifact remains | `src/api/__pycache__/websocket_manager.cpython-311.pyc` |

## Open Issues I Compared

In this section, I am looking at the issues that are still open and comparing them with the current codebase, mostly to see whether they still match the direction this tracked project has actually taken.

| Issue | Title | Status vs current repo | Matching files |
| --- | --- | --- | --- |
| #23 | Create React Frontend Skeleton | Implemented in current tree | `src/frontend/package.json`, `src/frontend/vite.config.js`, `src/frontend/index.html`, `src/frontend/src/main.jsx`, `src/frontend/src/App.jsx` |
| #24 | Build Fraud Monitoring Dashboard Components | Implemented in current tree | `src/frontend/src/App.jsx`, `src/frontend/src/styles.css`, `src/frontend/src/data/mockData.js` |
| #25 | Connect Frontend to WebSocket Alert Stream | Partially aligned; frontend now has a live alert layer and is ready for a real WebSocket client | `src/frontend/src/App.jsx`, `src/frontend/src/data/mockData.js` |
| #26 | End-to-End Integration Test (Backend + Frontend + Models) | Blocked by missing tracked backend/frontend source; no tracked end-to-end test source is present | No tracked integration test source available in current tree |
| #27 | Model Evaluation & Visualisation Notebook | Partially aligned; modality-specific notebooks exist, but no unified evaluation notebook is tracked | `backend/Fraud_Receipt_Detection_CV.ipynb`, `backend/Phisihing_Model_NLP.ipynb`, `backend/Midv2019_ID_Card_Fraud_Detection.ipynb` |
| #28 | Ethics & Responsible AI Section | Partially aligned; brief ethics notes exist, but no dedicated markdown/report section is tracked | `readme.md` |
| #29 | Final Report Writing (4 Pages + GitHub Evidence) | Not yet traceable from tracked files in current tree | No tracked report file found |
| #30 | Presentation Slides & Live Demo Practice | Not yet traceable from tracked files in current tree | No tracked slide deck found |

## Assignment Note

If I were assigning these issue notes based on the current project history, I would assign them to `@Ratselaft`.

One practical limitation in this session is that I can read the GitHub issues, but I still cannot edit the issue bodies or set assignees directly from here.
