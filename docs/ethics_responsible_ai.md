# Ethics and Responsible AI

I use this document to capture the main ethical risks, practical limitations,
and human-control expectations for the fraud detection system.

## Potential Bias in Datasets

- I rely on synthetic and public datasets rather than real bank production data, so class balance, language style, and user behaviour may not match real deployment conditions.
- The NLP component uses SMS spam data, which may overrepresent older phishing styles and underrepresent newer scam language.
- The CV component uses synthetic distortions and document datasets, so it may be better at spotting manipulated-looking images than subtle real-world forgeries.
- The transaction models may inherit sampling bias from whichever public fraud datasets are easiest to access.

## System Limitations

- I do not use real customer history, so behavioural features are simplified.
- Several model paths are still lightweight baseline models rather than production-tuned models.
- Some modalities can be degraded or unavailable depending on which artifacts are present at runtime.
- The system is strongest as a triage tool, not as a fully autonomous fraud adjudicator.

## PSD2 / SCA Awareness

- I treat high-risk scores as a signal for escalation rather than an automatic final verdict.
- In a regulated setting, high-risk outcomes should trigger stronger verification such as step-up authentication, manual review, or additional identity checks.
- I keep the design compatible with the idea that suspicious activity should prompt extra scrutiny, not silent customer denial without traceability.

## Importance of Human Monitoring

- I expect analysts or operators to review high-risk outcomes, especially when model confidence and readiness status disagree.
- I expose liveness, readiness, and model availability because operators need context before trusting the predictions.
- I treat the dashboard as a monitoring and investigation interface, not just a display layer.

## Model Cards

### Transaction model
- Purpose: estimate fraud risk from tabular transaction features
- Strength: fast and easy to serve
- Main risk: can miss fraud patterns that need richer identity context

### Anomaly model
- Purpose: flag unusual behaviour relative to normal transactions
- Strength: can surface novel fraud-like behaviour
- Main risk: false positives when legitimate behaviour changes quickly

### NLP model
- Purpose: estimate phishing/spam risk from message text
- Strength: lightweight and interpretable baseline
- Main risk: vocabulary drift and first-request cold start unless artifacts are preloaded

### CV model
- Purpose: estimate document manipulation risk from image evidence
- Strength: adds a non-transaction modality to the fraud score
- Main risk: synthetic distortions are not a full substitute for real forgery examples

## Responsible Use

- I would not use this system as the sole decision-maker for account blocking or legal enforcement.
- I would log model readiness and degraded states alongside predictions.
- I would review error patterns regularly to detect unfair treatment across user groups once real deployment data exists.
