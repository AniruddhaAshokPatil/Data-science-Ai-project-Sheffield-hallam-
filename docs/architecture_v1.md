# Incoming Transaction

<!-- I use this architecture sketch to keep the end-to-end flow easy to see
     at a glance before diving into code files. -->

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
