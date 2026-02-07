# **Real-Time Multimodal Financial Fraud Detection System**

A real-time machine learning application designed to detect fraudulent financial transactions using **structured data**, **behaviour‑based features**, **supervised ML**, **anomaly detection**, **Computer Vision (CV)**, and **Natural Language Processing (NLP)** — all displayed on a simple **live dashboard** that updates immediately when a suspicious transaction appears.

***

# **Problem Statement**

Fraud is one of the biggest threats in digital payments. Attackers move quickly, often exploiting systems that only analyse transactions after they have already happened. Batch‑processing fraud tools create dangerous delays where fraud may go undetected.

Our aim is to build a system that:

*   reacts to suspicious transactions **immediately**,
*   uses beginner‑friendly machine learning techniques,
*   enriches the analysis with **image** and **text** signals,
*   and presents everything in a clear, real‑time dashboard.

This project demonstrates how modern fraud systems combine multiple AI methods to support better decision‑making, even when implemented with simple, accessible tools.

***

# ** How the System Works **

Think of our system as a digital security guard:

### **1. A transaction arrives**

Our program receives each transaction instantly.

### **2. Behaviour checks**

The system calculates simple features such as:

*   spending speed,
*   unusual device,
*   amount spikes,
*   new merchant behaviour.

### **3. Machine Learning models evaluate fraud risk**

We use two models:

*   **Supervised ML model** (XGBoost or Logistic Regression)
*   **Anomaly model** (Isolation Forest)

### **4. CV & NLP add extra clues**

To make it multimodal:

*   **CV model**: checks if an uploaded document image looks fake
*   **NLP model**: checks if text messages look like phishing or scam attempts

These are small models trained on simple datasets — ** **.

### **5. Risk Score**

The models produce fraud‑risk scores.

### **6. Alert Engine**

If a transaction looks suspicious, the backend sends an **instant alert** to the dashboard.

### **7. Real-Time Dashboard**

A small React dashboard shows:

*   incoming transactions,
*   alerts,
*   CV/NLP results,
*   and model scores.


***

# **Key Features **

*   Real-time transaction scoring
*   Supervised ML with Python libraries
*   Anomaly detection using Isolation Forest
*   Behaviour and velocity features
*   Simple CV forgery‑detection model
*   Basic NLP phishing classifier
*   Live alerts through a lightweight backend
*   Clean dashboard built with React


# **Tech Stack **

### **Machine Learning**

*   Python
*   Pandas, NumPy
*   Scikit‑learn
*   XGBoost (optional)
*   TensorFlow/PyTorch (small CV model)
*   HuggingFace Transformers (small NLP model)

### **Backend**

*   FastAPI 
*   WebSockets for real-time updates

### **Frontend**

*   React
*   Recharts / Chart.js

### **Data**

*   IEEE‑CIS (tabular data)
*   Public small CV datasets (forgery detection)
*   Public phishing datasets (for NLP)

***

# **Multimodal AI Components**

## **📸 Computer Vision **

A small CNN model detects basic document/image manipulations.  
It is trained on a simple open-source dataset with:

*   resizing
*   normalization
*   basic augmentation

Output: a **forgery probability score**.

API: `/predict_document`

***

## ** NLP Phishing Detection **

A small DistilBERT text classifier detects phishing-like messages.

*   minimal text cleaning
*   simple train/val/test split
*   small dataset

API: `/predict_text`

***

# **Updated System Architecture **


    Incoming Transaction
            |
            v
    Feature Engineering
            |
            +-------------------+
            |                   |
    Supervised ML Model     Anomaly Model
    (XGBoost/LogReg)        (Isolation Forest)
            |                   |
            +--------+----------+
                     |
                Risk Scoring
            +--------+---------+
            |                  |
     CV Model             NLP Model
    (Document check)    (Text check)
            |                  |
            +---------+--------+
                      |
               Alert Engine (FastAPI)
                      |
                      v
            React Dashboard (live updates)





***

# **Group Members**

*   **Aniruddha Ashok Patil**
*   **Jibola Johnson Odekunle**
*   **Anderson Lucas Cachinavissa Aurelio**
*   **Onyinye Eugenia Asadu**
*   **Gaurav Sanjay Karnavar**
  
