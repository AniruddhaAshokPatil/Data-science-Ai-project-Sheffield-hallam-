# ShieldWise Final Report

## 1. Project Overview

ShieldWise is a gadget and electronics insurance claim fraud detection prototype. The project shows how a suspicious claim can be screened inside a working application, rather than only inside separate notebooks or isolated model scripts.

The system combines:

- claim text analysis
- structured policy and behavioural claim signals
- document and receipt evidence checks
- a FastAPI backend
- a React dashboard
- saved model artifacts and evaluation evidence

The main purpose is to demonstrate an end-to-end workflow. A policyholder can submit a claim, upload evidence, receive a tracked claim response, and an investigator can review claims through dashboard views and live alerts.

ShieldWise should be understood as a student prototype. It is not a production insurance fraud platform and should not be used to automatically reject real claims.

## 2. Insurance Fraud Problem

Gadget and electronics insurance claims can involve high-value devices such as laptops, smartphones, tablets, cameras, drones, gaming equipment, and specialist electronics. These claims often depend on a mixture of information:

- what the claimant says happened
- the value of the device
- the timing of the claim
- previous claim behaviour
- whether the receipt or repair evidence is convincing
- whether account or bank details changed near the claim

Fraud detection in this context is difficult because suspicious and genuine claims can look similar. A genuine customer may urgently need a replacement laptop for study or work. Another customer may have lost a receipt for a legitimate reason. At the same time, a suspicious claim may be carefully written and may include some evidence.

For this reason, ShieldWise does not try to make a final fraud decision. It calculates risk signals and uses them to support review. A high-risk result means the claim should be checked more carefully by a human reviewer.

## 3. Project Architecture

The project is organised as a full-stack web application.

### Backend

The backend is implemented with FastAPI in:

```text
src/api/
```

Important backend files include:

- `src/api/main.py` - creates the FastAPI app, configures CORS, and registers routers
- `src/api/config.py` - stores key data paths and runtime settings
- `src/api/db.py` - manages local SQLite tables for submitted claims and uploaded evidence
- `src/api/routers/auth.py` - handles demo login
- `src/api/routers/insurance.py` - exposes the insurance claim and dashboard endpoints
- `src/api/routers/health.py` - exposes health and readiness checks
- `src/api/services/insurance_data.py` - performs claim scoring and claim-history loading
- `src/api/services/document_risk.py` - checks uploaded evidence files
- `src/api/services/insurance_dashboard.py` - prepares dashboard summaries and queues
- `src/api/websocket_manager.py` - supports live alert streaming

### Frontend

The frontend is implemented with React and Vite in:

```text
src/frontend/
```

Important frontend files include:

- `src/frontend/src/main.jsx`
- `src/frontend/src/App.jsx`
- `src/frontend/src/styles.css`
- `src/frontend/package.json`
- `src/frontend/vite.config.js`

The frontend provides the user-facing workflow:

- public homepage
- policyholder login
- claim submission form
- evidence upload controls
- customer dashboard
- investigator dashboard
- review queue
- live risk alerts

### Data and Model Assets

The project uses data and model assets from:

```text
data/
backend/saved_models/
backend/receipts_models/
```

The small GitHub-friendly multimodal data pack is stored in:

```text
data/sample/
```

This sample pack allows the project to be understood without committing large raw datasets.

## 4. Data Preparation

ShieldWise uses several data types because the claim-review problem is multimodal.

### Structured Claim Data

Structured claim data is used for behavioural scoring and dashboard summaries. The main full-data path is:

```text
data/raw/insurance_claims/claim_history_detailed.csv
```

If this file is not available, the backend falls back to:

```text
data/sample/claims/claim_history_sample.csv
```

This fallback makes the repository easier to run from a clean clone.

Structured fields include claim amount, device value, previous claims, recent account changes, receipt flags, document flags, and final review labels.

### Claim Email Ham/Spam Data

The claim-language dataset is stored in:

```text
data/raw/nlp/claim_email_ham_spam.csv
```

It contains 240 rows:

- 120 ham rows
- 120 spam rows

The data is focused on gadget and equipment insurance. The current claim email CSV uses fields that match the claim form, including:

- claimant name and email
- policy type and coverage tier
- device category
- incident type
- claim amount and device value
- prior claims
- claims in the last 12 months
- days since policy start
- email subject
- message body
- binary behavioural and evidence flags
- ham/spam label
- language risk band

The incident type coverage now includes 12 categories:

- `accessory_damage`
- `accidental_damage`
- `battery_failure`
- `electrical_fault`
- `in_transit_damage`
- `liquid_spill`
- `loss`
- `malicious_damage`
- `power_surge`
- `screen_damage`
- `theft`
- `water_damage`

The dataset can be regenerated with:

```bash
python scripts/rebuild_claim_email_dataset.py
```

The clean NLP corpus is prepared with:

```bash
python src/data/clean_sms_dataset.py
```

The NLP models are trained with:

```bash
python scripts/train_claim_email_nlp_model.py
```

### Evidence and Document Data

The project includes a small multimodal sample pack in:

```text
data/sample/
```

It contains:

- sample claim email rows
- sample claim-history rows
- receipt images
- a repair quote PDF
- a synthetic ID-style image
- evidence manifests
- a multimodal index linking claims, text, tabular data, and evidence files

The sample pack can be regenerated with:

```bash
python scripts/prepare_sample_multimodal_data.py
```

The sample evidence files are intentionally synthetic and small. They are included so a marker can understand the multimodal workflow without needing the full research image datasets.

## 5. Runtime Logic

When the application runs, a claim is scored using three main components.

### Email Language Risk

The claim story is scored using saved NLP assets from:

```text
backend/saved_models/
```

Important files include:

- `mnb_model.pkl`
- `rf_model.pkl`
- `tfidf_vectorizer.pkl`
- `chi2_selector.pkl`
- `phishing_keywords.json`
- `stat_feature_cols.json`

The backend combines model probability with heuristic signals so the output is not unrealistically constant. The score is intended to detect suspicious language patterns such as urgent payout pressure, vague event detail, or payment-change wording.

### Behavioural Risk

Behavioural risk is calculated from structured claim features in `src/api/services/insurance_data.py`.

Important behavioural signals include:

- recent high-value purchase
- unusual spending spike
- login location changed
- multiple devices in 7 days
- address changed recently
- phone changed recently
- bank details changed recently
- late-night submission
- weekend submission
- prior claims
- claims in the last 12 months
- claim amount compared with device value
- very new policy

The project uses an explainable scoring method rather than a hidden black-box tabular model. This makes the risk calculation easier to discuss in the report and demo.

### Document Risk

Document and evidence risk is handled in:

```text
src/api/services/document_risk.py
```

The runtime document checks are lightweight and rule-based. They look for:

- missing evidence
- duplicate evidence by SHA-256 hash
- unusually small images
- extreme image aspect ratios
- low-colour image modes
- unreadable or corrupt images
- unusually small PDFs

The project also retains supporting CV model artifacts and notebooks, but the running API uses lightweight checks for speed, clarity, and reliability during the demo.

### Final Risk Score

The final score combines the three components:

```python
total_risk = (email_risk * 0.30) + (behavioural_risk * 0.42) + (document_risk * 0.28)
```

Risk labels are:

| Final Score | Label |
| --- | --- |
| `>= 0.65` | High |
| `>= 0.32` | Medium / Review |
| `< 0.32` | Low |

The thresholds are intentionally sensitive because the system is designed to flag claims for review, not to reject them automatically.

## 6. Testing

The main automated test file is:

```text
tests/test_api_insurance.py
```

It covers key API behaviour, including:

- authentication
- protected endpoints
- claim submission
- claim scoring
- dashboard responses
- evidence handling paths
- WebSocket alert behaviour

The test command is:

```bash
python3 -m pytest tests/test_api_insurance.py
```

Current result:

```text
18 passed
```

The repository also includes a project validation script:

```bash
python3 scripts/validate_project.py
```

This checks important files, model artifacts, data paths, package availability, and configuration files.

## 7. Results

### NLP Results

The current NLP training metrics are stored in:

```text
backend/saved_models/nlp_metrics.json
```

Current dataset:

- path: `data/raw/nlp/claim_email_ham_spam.csv`
- rows: 240
- training rows: 192
- test rows: 48
- selected features: 220

Current model metrics:

| Model | Accuracy | Precision | Recall | F1 | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| MultinomialNB | 0.7708 | 1.0000 | 0.5417 | 0.7027 | 0.9896 |
| RandomForest | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

These results should be interpreted carefully. The dataset is generated for the project and is useful for demonstrating the NLP workflow, but it is not proof of real-world insurer performance.

The runtime scoring distribution is intentionally varied so ham and spam messages do not all receive identical scores. The current pattern keeps ham generally low and spam generally higher, while still allowing medium-risk cases.

### Receipt / CV Supporting Results

Receipt model metrics are stored in:

```text
backend/receipts_models/cv_metrics.json
```

Current stored metrics:

| Model | Accuracy | Precision | Recall | F1 | ROC AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| MobileNetV2 | 0.9937 | 0.9937 | 1.0000 | 0.9968 | 0.9108 |
| ResNet50 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | N/A |

These metrics support the project research narrative. The live API does not depend on heavy image-model inference during normal demo use; it uses lightweight document checks.

### System Result

The main result of the project is an integrated working prototype. The system connects:

```text
data -> models -> API -> frontend -> claim review dashboard -> live alerts
```

This is the main contribution. The project is not only a model notebook; it is a working insurance claim workflow.

## 8. Ethics and Responsible AI

The responsible AI position is documented separately in:

```text
docs/ETHICS_RESPONSIBLE_AI.md
```

The key ethical point is that ShieldWise should be used as a triage tool. A high score means a claim should be reviewed, not automatically rejected.

The main ethical risks are:

- false positives affecting genuine claimants
- false negatives missing carefully written suspicious claims
- fairness issues from behavioural or language-based signals
- sensitive evidence handling
- over-interpreting a prototype score as proof

The project therefore uses careful language such as "flagged for review" and "high-risk claim" rather than claiming that the system proves fraud.

## 9. Limitations

The main limitations are:

- the NLP dataset is generated for the project and may not match real insurer communication
- the multimodal sample pack is small and curated
- the receipt and ID evidence workflow is simplified at runtime
- the CV artifacts are supporting research assets rather than production runtime services
- the model has not been tested across real demographic groups
- the system has no production drift monitoring
- SQLite is used for local demonstration rather than production storage
- evidence storage is local and not suitable for real sensitive customer documents
- risk thresholds are selected for demonstration clarity rather than insurer calibration

These limitations are important because fraud detection has real consequences for customers. The project should be presented as a proof of concept, not as a deployment-ready decision system.

## 10. Conclusion

ShieldWise demonstrates how AI can support gadget and electronics insurance claim review by combining text, structured claim behaviour, and document evidence. The system includes a working FastAPI backend, a React frontend, saved model artifacts, risk scoring, dashboards, evidence checks, and live alerts.

The project shows the value of integrating multiple signals rather than relying on one model or one dataset. It also shows why responsible use matters. A risk score can help prioritise review, but it cannot replace human judgement.

Overall, ShieldWise is best described as an educational, end-to-end fraud triage prototype. It successfully demonstrates data preparation, model integration, API design, frontend workflow, testing, evaluation evidence, and responsible AI documentation for a gadget insurance claim scenario.

