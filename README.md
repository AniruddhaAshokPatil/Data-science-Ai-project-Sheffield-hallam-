## Real-Time Financial Fraud Detection System

A real-time machine learning system designed to detect fraudulent financial transactions using structured data, anomaly detection, behavioural modelling, and supervised learning — complete with live alerts and an interactive monitoring dashboard.

### Problem Statement

Financial fraud continues to be a major challenge for banks, fintech companies, and customers. Every year, billions are lost to increasingly fast, adaptive, and sophisticated fraud schemes. As digital payments explode in popularity, attackers evolve just as quickly — exploiting weaknesses in systems that cannot respond fast enough.

Most traditional fraud detection setups work in batches, meaning they analyse transactions only after they’ve already happened. This creates a dangerous delay where fraudulent activity can slip through, harming customers and damaging institutional trust.

This project solves that problem by building a real-time fraud detection system. It analyses each transaction the moment it occurs, identifies suspicious behaviour instantly, and raises immediate alerts. By combining supervised machine learning with anomaly detection and velocity-based behavioural features, the system aims to reduce fraud while protecting genuine customers in a scalable, production-inspired environment.

### How the System Works

Imagine a security guard watching a busy mall:

1. A transaction comes in

Someone tries to buy something — the system “notices” this immediately.

2. Stream processor watches in real time

Just like the security guard’s eyes, it monitors activity as it happens.

3. Feature engineering — the system asks smart questions:

Is this person spending faster than they normally do?
Is the purchase happening in a new or unusual location?
Is the device unfamiliar?
Does this pattern resemble something suspicious we’ve seen before?

4. Machine learning models evaluate the behaviour

One model checks if the transaction matches known fraud patterns.
Another model (anomaly detector) checks if the behaviour looks unusual, even if it’s something completely new.

5. Risk score is calculated

The system assigns the transaction a “danger score” based on all the evidence.

6. Alert engine triggers warnings

If the score is high, analysts are alerted instantly. There is no delays.

7. Dashboard displays everything live

Every transaction, alert, and risk score appears in real time on an interactive dashboard.

### Key Features

Real-time transaction processing,
Fraud detection using both machine learning and anomaly detection,
Behavioural and velocity-based feature engineering,
Transaction-level risk scoring,
Live fraud alerts delivered instantly,
Interactive dashboard for analysts,
Scalable design modeled after real financial systems

###  Tech Stack

#### Machine Learning

Python,
Pandas,
NumPy,
Scikit-learn,
XGBoost,
Isolation Forest

#### Backend

FastAPI,
WebSockets

#### Streaming & Storage

Apache Kafka, 
PostgreSQL,
Redis,

#### Frontend
React
Chart.js / Recharts

###  System Architecture

The system processes transactions through the following real-time pipeline:

Transaction
(The firehose — raw incoming financial activity)
⬇  

Stream Processor
(Receives and processes each transaction instantly)
⬇  

Feature Engineering
(Builds behavioural signals — spending speed, unusual location/device, pattern changes)
⬇  

ML Models (Classification + Anomaly Detection)
(Two AI models working together to evaluate risk)
⬇  

Risk Scoring
(Combines evidence to determine overall suspiciousness)
⬇  

Alert Engine
(Sends high-risk events to analysts immediately)
⬇  

Live Dashboard
(Real-time visualization of the entire fraud detection pipeline)

###  Implementation Notes

This project is actively developed and intentionally iterative.
The technologies listed represent the current stack, but components may evolve as we refine performance, scalability, and learning outcomes. All updates will follow industry best practices and remain aligned with the project’s core objective: building a real-time, production-inspired fraud detection system.

###  Group Members

Aniruddha Ashok Patil,
Jibola Johnson Odekunle,
Anderson Lucas Cachinavissa Aurelio,
Onyinye Eugenia Asadu,
Gaurav Sanjay Karnavar
