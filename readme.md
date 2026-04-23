# **ShieldWise - Gadget Insurance Claim Fraud Detection Platform**

ShieldWise is my gadget and electronics insurance fraud detection project. I built it to show how suspicious device claims can be screened inside a working application, not only inside separate model notebooks.

The project brings together a FastAPI backend, a React dashboard, supporting model work, and device-claim data so the workflow can be tested from policyholder submission through to investigator review.

---

## **What ShieldWise Does**

ShieldWise simulates how a gadget insurer, electronics warranty provider, or device-protection company could receive claims, check the evidence, and highlight claims that may need closer review.

At a high level, it:

* Accepts gadget and electronics claims through a structured submission form
* Allows upload of purchase receipts, repair invoices, and claimant ID cards
* Analyses claim text for suspicious language patterns
* Evaluates behavioural signals from device claim history
* Performs lightweight document checks on uploaded receipt and ID evidence
* Streams live alerts to investigators
* Displays results in both customer and investigator dashboards

The main point of the project is the full workflow: data, models, API, interface, and alerts working together.

---

## **System Overview**

The platform is split into two main parts:

### **Backend (FastAPI)**

Located in `src/api/`

Handles:

* Gadget claim intake and validation
* Risk scoring (language + behaviour + document checks)
* Data storage using SQLite
* WebSocket streaming for real-time alerts

---

### **Frontend (React + Vite)**

Located in `src/frontend/`

Provides:

* Public homepage
* Policyholder dashboard (submit + track device claims)
* Investigator dashboard (review + alerts)

---

### **Live Alerts (WebSockets)**

* Investigators receive real-time updates when high-risk claims are submitted
* Keeps the system responsive instead of relying on batch checks

---

## **How Risk Scoring Works**

ShieldWise combines several signals instead of depending on one score or one model.

Conceptually:

$$
Risk_{total} = w_1 \cdot Risk_{behaviour} + w_2 \cdot Risk_{language} + w_3 \cdot Risk_{document}
$$

### **1. Behavioural Risk**

* Based on device claim patterns and history
* Looks at frequency, timing, account changes, and unusual high-value electronics activity

### **2. Language Risk (NLP)**

* Analyses gadget claim descriptions and emails
* Flags suspicious wording patterns

### **3. Document Risk (CV-inspired, rule-based runtime)**

* Checks uploaded receipts, repair invoices, and ID documents
* Focuses on evidence consistency rather than heavy model inference during the live demo

---

## **Datasets Used**

This project uses a mix of structured, text, and image data. Each dataset is used with a clear purpose and limitation.

---

### **Gadget Insurance Claim Data (Core System Data)**

Located in:

```
data/raw/insurance_claims/
```

Files:

* `claim_history_detailed.csv`
* `submitted_claims.csv`

Used for:

* Gadget claim workflows
* Behavioural risk scoring
* Dashboard visualisation

---

### **Claim Language Dataset (NLP)**

```
data/raw/nlp/claim_email_ham_spam.csv
```

Used for:

* Training the claim-language risk component for device-related claim messages

Important note:

* This dataset is **synthetically generated**
* I use it for prototyping and explanation, not as proof of real insurer-level performance

---

### **Receipt Dataset (Device Evidence / CV Context)**

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

* Purchase receipt structure understanding
* Supporting evidence validation logic for device claims

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

* Understanding ID document variability
* Supporting claimant identity checks for high-value gadget claims

---

### **Important Data Note**

Not all data in this project reflects real-world distributions.

* NLP dataset → synthetic
* Receipt dataset → small sample (200 images)
* CV models → supporting, not production-scale

This is intentional. My focus is on **system design and integration**, while being honest about the limits of the available datasets.

---

## **Repository Structure**

```
.
├── backend/                        # Stored model artifacts (NLP, receipt research)
├── data/
│   ├── raw/insurance_claims/       # Core structured gadget claim data
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

## Evaluation Workflow

A consolidated evaluation notebook for the current ShieldWise submission is available at [backend/ShieldWise_Evaluation_Workflow.ipynb](backend/ShieldWise_Evaluation_Workflow.ipynb). I use it to bring together the retained NLP metrics, receipt-model metrics, and the final submission explanation in one place.

---

## **Design Decisions (Why This Approach)**

* I focused on the **real gadget claim workflow first**, then connected the model work around it
* I kept the live document checks lightweight so the app remains quick during a demo
* I used WebSockets to show how investigators can receive live alerts
* I separated the backend and frontend so the project is easier to understand and extend

---

## **Known Limitations**

* Synthetic NLP data may not generalise
* Small receipt dataset limits deep CV modelling
* No continuous model monitoring (no drift detection yet)
* SQLite used for simplicity, not production scale

---

## **Final Note**

ShieldWise is designed to show how gadget claim fraud detection works **inside a system**, not just inside a notebook.

It connects:

* data → models → API → user interface → alerts

That integration is the main contribution of the project.
