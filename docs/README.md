# Real-Time Multimodal Financial Fraud Detection System

<!-- I use this document as the high-level project explanation, so it focuses
     on the system idea, the architecture, and how the modalities connect. -->

A real-time, multimodal machine learning system designed to detect fraudulent financial activity by combining **transaction behaviour**, **document verification (Computer Vision)**, and **communication analysis (NLP)**.

The system processes transactions as they arrive, computes a **unified fraud risk score**, and generates alerts through a live dashboard.

---

# Problem Statement

Fraud in digital payments is increasingly **multi-vector**. Systems that rely only on transaction data or batch processing introduce delays and miss important contextual signals such as:

* manipulated identity documents
* phishing or scam communications
* behavioural anomalies across sessions

This project builds a **real-time fraud detection pipeline** that integrates multiple AI components into a single decision system.

---

# Project Objective

The system aims to:

* detect fraudulent transactions **in real time**
* use **interpretable, beginner-friendly ML models**
* incorporate **image (CV) and text (NLP) signals**
* provide a **live dashboard for monitoring risk**
* demonstrate **multimodal AI integration in fraud detection**

---

# System Overview (Multimodal Design)

The system combines three independent fraud signals:

| Modality           | Function                         | Output                           |
| ------------------ | -------------------------------- | -------------------------------- |
| Transaction Models | Behavioural fraud detection      | Fraud probability                |
| Computer Vision    | Document integrity approximation | Distortion / forgery probability |
| NLP                | Phishing detection               | Spam probability                 |

These outputs are combined into a **single risk score** used for final decision-making.

---

# End-to-End Flow (Example)

```text
Transaction received
→ Supervised Score = 0.72
→ Anomaly Score = 0.65
→ CV Score = 0.20
→ NLP Score = 0.80

Final Score = 0.62
→ Fraud (threshold = 0.6)
```

---

# System Architecture

```text
Incoming Transaction
        |
        v
Feature Engineering
        |
        v
+--------------------------------------+
| Supervised ML Model (S_sup)          |
| Anomaly Model (S_anom)               |
| CV Model (S_cv)                     |
| NLP Model (S_nlp)                   |
+--------------------------------------+
                    |
                    v
         Multimodal Risk Fusion
                    |
                    v
           Alert Engine (FastAPI)
                    |
                    v
         React Dashboard (Live)
```

---

# How the System Works

### 1. Transaction Ingestion

Transactions are received via FastAPI endpoints and processed individually.

---

### 2. Feature Engineering

Behavioural features are derived from transaction data:

* velocity (time between transactions)
* spending deviation
* device and IP anomalies
* merchant interaction patterns

These features are either:

* provided directly in the dataset, or
* computed using rolling transaction windows

---

### 3. Parallel Model Inference

All models operate independently:

* **Supervised Model (XGBoost / Logistic Regression)**
  Outputs probability: ( S_{sup} )

* **Anomaly Detection (Isolation Forest)**
  Outputs anomaly score: ( S_{anom} )

* **CV Model (Document Verification)**
  Detects visual distortions → ( S_{cv} )

* **NLP Model (Phishing Detection)**
  Classifies scam messages → ( S_{nlp} )

---

### 4. Multimodal Risk Fusion

[
Score_{total} = w_1 S_{sup} + w_2 S_{anom} + w_3 S_{cv} + w_4 S_{nlp}
]

Example weights:

* ( w_1 = 0.4 ), ( w_2 = 0.3 ), ( w_3 = 0.2 ), ( w_4 = 0.1 )

### Decision Rule

[
Fraud =
\begin{cases}
1 & \text{if } Score_{total} > \tau \
0 & \text{otherwise}
\end{cases}
]

---

# Implementation Mapping

| Proposal Component | Implementation               |
| ------------------ | ---------------------------- |
| Transaction ML     | `src/transaction/`           |
| Anomaly Detection  | `src/anomaly/`               |
| CV Model           | `src/cv/`                    |
| NLP Model          | `src/nlp/`                   |
| Risk Fusion        | `src/fusion/risk_scoring.py` |
| Backend API        | `src/api/main.py`            |
| Dashboard          | `frontend/`                  |

---

# Core Fusion Logic (Code)

```python
# I am combining outputs from all models into a single fraud score
def compute_risk_score(sup, anom, cv, nlp):
    
    # I am assigning weights to each modality
    w1, w2, w3, w4 = 0.4, 0.3, 0.2, 0.1
    
    # I am computing the final weighted score
    score = (w1 * sup) + (w2 * anom) + (w3 * cv) + (w4 * nlp)
    
    return score


# I am defining the classification rule
def classify_transaction(score, threshold=0.6):
    
    # I am comparing score with threshold
    if score > threshold:
        return 1
    else:
        return 0
```

---

# Datasets

### Transaction Data

* Financial Transactions Dataset (Kaggle, ~5M records)
* Credit Card Fraud Dataset (used for validation)

### Computer Vision

* MIDV-500 / MIDV-2019
* Synthetic distortions applied to simulate manipulation

### NLP

* SMS Spam Collection Dataset
* Binary classification: ham vs spam

---

# API Design

### Transaction Prediction

```json
POST /predict_transaction

Input:
{
  "amount": 120.5,
  "device": "mobile",
  "location": "UK"
}

Output:
{
  "fraud_score": 0.72,
  "prediction": 1
}
```

---

### Document Prediction

```json
POST /predict_document

Output:
{
  "cv_score": 0.30
}
```

---

### Text Prediction

```json
POST /predict_text

Output:
{
  "nlp_score": 0.85
}
```

---

### Alerts

* WebSocket endpoint: `/alerts`
* Streams real-time fraud alerts

---

# Real-Time Processing

* Transactions are processed via API requests
* Each request triggers model inference
* Alerts are streamed using WebSockets
* A sequential loop can simulate streaming input

---

# Evaluation Strategy

### Transaction Models

* Precision, Recall, F1-score
* ROC-AUC
* PRAUC, MCC

### CV Model

* Accuracy
* Confusion matrix

### NLP Model

* Accuracy
* Precision / Recall

### System-Level

* Latency per request
* Throughput
* Alert accuracy

---

# How to Run the Project

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Run Backend (FastAPI)

```bash
uvicorn src.api.main:app --reload
```

---

### 3. Run Frontend

```bash
cd frontend
npm install
npm start
```

---

### 4. Access Application

* API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Frontend: [http://localhost:3000](http://localhost:3000)

---

# Limitations

* Datasets are independent (no shared entity linkage)
* CV model detects distortions, not real-world forgery
* Real-time behaviour is simulated rather than deployed at scale

---

# Key Features

* Real-time fraud scoring
* Hybrid ML (supervised + anomaly detection)
* Multimodal integration (transaction + CV + NLP)
* Explainable scoring
* Modular architecture
* Live alert system

---

# Tech Stack

### Machine Learning

* Python, Pandas, NumPy
* Scikit-learn, XGBoost
* TensorFlow / PyTorch
* HuggingFace Transformers

### Backend

* FastAPI
* WebSockets

### Frontend

* React
* Recharts / Chart.js

---

# Group Members

* Aniruddha Ashok Patil
* Jibola Johnson Odekunle
* Anderson Lucas Cachinavissa Aurelio
* Onyinye Eugenia Asadu
* Gaurav Sanjay Karnavar
