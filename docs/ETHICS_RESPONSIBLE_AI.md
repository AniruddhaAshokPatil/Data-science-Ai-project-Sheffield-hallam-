# ShieldWise Ethics and Responsible AI

ShieldWise is a student prototype for reviewing gadget and electronics insurance claims. It shows how an insurer could combine three kinds of information:

- the written claim message
- structured claim details such as device value, prior claims, and account changes
- uploaded evidence such as receipts, repair invoices, and ID-style documents

The system gives each claim a risk score and places it into a review category. This can help demonstrate how AI might support claim triage. However, it must be understood carefully: ShieldWise does not prove that a customer has committed fraud, and it should not be used to automatically reject a real insurance claim.

## Purpose of the System

The purpose of ShieldWise is to demonstrate a workflow. It is useful for showing how a claim can move from submission, through risk scoring, into an investigator dashboard.

In this project, a higher score means:

> This claim has warning signs and should be reviewed more carefully.

It does not mean:

> This claimant is dishonest.

That difference matters. Fraud detection systems can affect real people, so the language around them needs to be careful and fair.

ShieldWise is suitable for:

- an academic demonstration
- explaining how multimodal data can support claim review
- showing how text, behaviour, and documents can be combined
- helping a reviewer understand why a claim may need attention

ShieldWise is not suitable for:

- automatic claim rejection
- final payout decisions
- real customer assessment without further testing
- replacing trained insurance investigators
- production use without legal, ethical, and security review

## Human Oversight

Any system like ShieldWise should keep a human in control. The system can highlight risk, but a person should make the final decision.

For example, if ShieldWise marks a claim as high risk, the correct next step is not to reject it immediately. The correct next step is to review the claim more carefully. A human investigator should look at the full context, such as:

- what the claimant wrote
- whether the receipt or invoice looks complete
- whether any missing evidence can be explained
- whether account changes were normal
- whether the customer should be asked for more information

A real insurer should also record the final reason for a decision separately from the AI score. This is important because a score is only a signal. It is not a complete explanation on its own.

## False Positives

A false positive happens when the system flags a genuine claim as suspicious.

This is one of the most important ethical risks in this project. A genuine customer may be delayed, questioned, or treated unfairly if the system is too sensitive.

Examples of genuine claims that could look suspicious include:

- a student urgently claiming for a laptop because they need it for coursework
- a worker submitting a late-night claim because they were busy during the day
- a customer changing bank details for normal personal reasons
- a customer losing a receipt because the device was bought months ago
- a claim with missing evidence because the customer is waiting for a repair shop

These examples show why ShieldWise should not be treated as a final judge. A high score should trigger review, not punishment.

## False Negatives

A false negative happens when the system gives a low score to a claim that is actually suspicious.

This can also happen. A dishonest claimant may write calmly, avoid obvious urgent language, include some evidence, or copy realistic claim wording. This means a low score should not be treated as a guarantee that a claim is safe.

The system is therefore best understood as one part of a wider review process. It can help prioritise claims, but it should not be the only control used by an insurer.

## Fairness Concerns

Fairness is important because insurance customers have different circumstances. A signal that looks suspicious for one person may be normal for another.

For example:

- Students, freelancers, and technology workers may use several devices in a short time.
- People who travel, commute, or study away from home may have changing login locations.
- Some people may buy second-hand devices and not have full receipts.
- A person under stress may write a claim message that sounds urgent or unclear.
- Customers whose first language is not English may write differently from the examples used in training data.

ShieldWise does not directly use protected characteristics such as race, religion, gender, or disability. However, fairness issues can still appear indirectly. For example, postcode, device behaviour, language style, or evidence availability could become proxy signals if used carelessly.

Before any real deployment, the system would need fairness testing across different customer groups. It would also need clear rules to make sure people are not disadvantaged because of normal life circumstances.

## Explainability

ShieldWise is designed to be understandable. Instead of showing only one final number, it separates risk into three parts:

- `email_language_risk_score`
- `behavioural_risk_score`
- `document_risk_score`

This helps a reviewer see the reason a claim was flagged. For example:

- the message may contain urgent payout pressure
- the claim may follow recent account changes
- the receipt may be missing, duplicated, or visually suspicious

The scoring method is explained in `docs/RISK_SCORING_METHODOLOGY.md`.

However, explainability also has a limit. Explaining why a claim was flagged does not prove fraud. It only explains which signals increased the risk score.

## Evidence Handling and Privacy

Insurance evidence can be sensitive. Receipts, repair invoices, device photos, and ID documents may contain personal information. A real insurer would need strong privacy and security controls.

Responsible evidence handling would require:

- secure storage
- access control so only authorised staff can view evidence
- encryption for stored files and uploaded files
- audit logs showing who accessed evidence
- retention rules so evidence is not kept longer than necessary
- deletion processes when files are no longer needed
- clear privacy notices explaining how evidence is used

In this student project, uploaded files are stored locally for demonstration. The files in `data/sample/evidence/` are synthetic examples, not real customer documents. This keeps the demo safer and avoids exposing real personal data.

## Data and Model Limitations

The project data is suitable for demonstrating the workflow, but it is not enough to prove real-world performance.

Important limitations include:

- the claim email ham/spam dataset is generated for this project
- the sample multimodal data pack is small and curated
- real insurance claim messages would be more varied and less predictable
- the document checks are lightweight at runtime
- the saved CV model artifacts support the project research, but the running API mainly uses rule-based evidence checks
- the thresholds are chosen for a clear demo, not calibrated from real insurer outcomes
- the model has not been tested for demographic fairness
- there is no production monitoring for drift or changing fraud patterns

These limitations do not make the project invalid. They simply define its correct scope. ShieldWise is a prototype that demonstrates design, integration, and responsible thinking. It is not a validated commercial fraud platform.

## Prototype Compared With a Real Insurer System

A real insurer would need much more work before using a system like this. That would include:

- large representative claim datasets
- independent model validation
- bias and fairness testing
- legal review
- privacy impact assessment
- secure document storage
- staff training
- audit trails
- appeal and complaint processes
- ongoing monitoring after deployment

In a real organisation, customers should also be able to challenge a decision, provide extra evidence, and understand the main reason their claim was delayed or reviewed.

## Responsible Language

The way the system is described is important. The project should avoid language that makes the AI sound more certain than it is.

Better wording:

- "high-risk claim"
- "flagged for review"
- "suspicious indicators"
- "requires human investigation"
- "possible evidence issue"

Wording to avoid:

- "fraudster"
- "fraud proven"
- "automatic rejection"
- "the AI decided"
- "fake claim" unless this has been confirmed by a human investigation

This protects claimants and makes the project more accurate.

## Final Position

The responsible way to describe ShieldWise is:

> ShieldWise is an AI-assisted triage prototype. It helps identify claims that may need closer review, but it does not decide whether a claimant is honest or dishonest.

This is the key ethical point of the project. The system can support human judgement, but it should not replace it.

