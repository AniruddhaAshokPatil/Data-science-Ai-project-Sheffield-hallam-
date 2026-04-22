# **ShieldWise — Insurance Claim Fraud Detection Platform**

ShieldWise is a practical fraud detection system built around a real insurance workflow. It focuses on how claims are submitted, reviewed, and flagged in a live environment rather than just training models in isolation.

The project combines a backend API, a frontend dashboard, and supporting data pipelines into a single working system.

---

## **What ShieldWise Does**

ShieldWise simulates how an insurer would handle incoming claims and identify risk early.

At a high level, it:

* Accepts insurance claims through a structured submission form
* Allows optional upload of supporting evidence (e.g. receipts)
* Analyses claim text for suspicious language patterns
* Evaluates behavioural signals from claim history
* Performs lightweight document checks on uploaded evidence
* Streams live alerts to investigators
* Displays results in both customer and investigator dashboards

This is not just a model project — it is an **end-to-end workflow system**.

---

## **System Overview**

The platform is split into two main parts:

### **Backend (FastAPI)**

Located in `src/api/`

Handles:

* Claim intake and validation
* Risk scoring (language + behaviour + document checks)
* Data storage using SQLite
* WebSocket streaming for real-time alerts

---

### **Frontend (React + Vite)**

Located in `src/frontend/`

Provides:

* Public homepage
* Policyholder dashboard (submit + track claims)
* Investigator dashboard (review + alerts)

---

### **Live Alerts (WebSockets)**

* Investigators receive real-time updates when high-risk claims are submitted
* Keeps the system responsive instead of relying on batch checks

---

## **How Risk Scoring Works**

ShieldWise combines multiple signals rather than relying on a single model.

Conceptually:

$$
Risk_{total} = w_1 \cdot Risk_{behaviour} + w_2 \cdot Risk_{language} + w_3 \cdot Risk_{document}
$$

### **1. Behavioural Risk**

* Based on claim patterns and history
* Looks at frequency, timing, and unusual activity

### **2. Language Risk (NLP)**

* Analyses claim descriptions and emails
* Flags suspicious wording patterns

### **3. Document Risk (CV-inspired, rule-based runtime)**

* Checks uploaded receipts or documents
* Focuses on structure consistency rather than heavy model inference

---

## **Datasets Used**

This project uses a mix of structured, text, and image data. Each dataset is used with a clear purpose and limitation.

---

### **Insurance Claim Data (Core System Data)**

Located in:

```
data/raw/insurance_claims/
```

Files:

* `claim_history_detailed.csv`
* `submitted_claims.csv`

Used for:

* Claim workflows
* Behavioural risk scoring
* Dashboard visualisation

---

### **Claim Language Dataset (NLP)**

```
data/raw/nlp/claim_email_ham_spam.csv
```

Used for:

* Training the claim-language risk component

Important note:

* This dataset is **synthetically generated**
* It is used for prototyping, not as a real-world benchmark

---

### **Receipt Dataset (Evidence / CV Context)**

**Dataset:** ExpressExpense SRD
**Source:** [https://expressexpense.com](https://expressexpense.com)
**License:** MIT

Details:

* 200 high-resolution receipt images
* Includes:

  * business name
  * address
  * itemised purchases
  * subtotal, tax, total

Used for:

* Document structure understanding
* Supporting evidence validation logic

Citation:

```
ExpressExpense SRD Dataset. Retrieved from https://expressexpense.com
Licensed under MIT License.
```

---

### **Identity Document Dataset (Supporting CV Research)**

**Dataset:** MIDV-500 / MIDV-2019

Details:

* 500 video clips
* 50 document types (IDs, passports, licences)
* Includes challenging conditions (blur, low light)

Used for:

* Understanding document variability
* Supporting document fraud concepts

---

### **Important Data Note**

Not all data in this project reflects real-world distributions.

* NLP dataset → synthetic
* Receipt dataset → small sample (200 images)
* CV models → supporting, not production-scale

This is intentional. The focus is on **system design and integration**, not dataset scale.

---

## **Repository Structure**

```
.
├── backend/                        # Stored model artifacts (NLP, receipt research)
├── data/
│   ├── raw/insurance_claims/       # Core structured claim data
│   ├── raw/nlp/                    # NLP dataset
│   └── processed/                  # Runtime outputs + SQLite DB
├── docs/
│   ├── ISSUE_ALIGNMENT.md
│   ├── INSURANCE_CLAIM_SAMPLES.md
│   └── PROJECT_TRACEABILITY.md
├── scripts/
│   ├── rebuild_missing_models.py
│   ├── train_claim_email_nlp_model.py
│   └── validate_project.py
├── src/
│   ├── api/                        # FastAPI backend
│   └── frontend/                   # React frontend
└── tests/
    └── test_api_insurance.py
```

---

## **How To Run**

### **Full System**

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m spacy download en_core_web_sm

cd src/frontend
npm install
cd ../..

chmod +x run_all.sh
./run_all.sh
```

Access:

* Frontend → [http://localhost:5173](http://localhost:5173)
* Backend → [http://localhost:8000](http://localhost:8000)
* API Docs → [http://localhost:8000/docs](http://localhost:8000/docs)

---

### **Backend Only**

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

### **Frontend Only**

```bash
cd src/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

---

## **Demo Accounts**

* Policyholder: `demo_user / UserPass123!`
* Investigator: `investigator_anna / InvestigatorPass123!`

---

## **Testing**

Run API tests:

```bash
python3 -m pytest tests/test_api_insurance.py
```

Validate project health:

```bash
python3 scripts/validate_project.py
```

---

## **Design Decisions (Why This Approach)**

* Focus on **real workflow first**, models second
* Keep document checks lightweight to avoid latency issues
* Use WebSockets to simulate operational alert systems
* Separate backend and frontend clearly for scalability

---

## **Known Limitations**

* Synthetic NLP data may not generalise
* Small receipt dataset limits deep CV modelling
* No continuous model monitoring (no drift detection yet)
* SQLite used for simplicity, not production scale

---

## **Final Note**

ShieldWise is designed to show how fraud detection works **inside a system**, not just inside a notebook.

It connects:

* data → models → API → user interface → alerts

That integration is the core of the project.
