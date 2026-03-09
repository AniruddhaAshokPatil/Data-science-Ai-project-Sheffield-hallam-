# Incoming Transaction

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