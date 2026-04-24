# ShieldWise Multimodal Sample Data

This folder contains a small, commit-friendly demo pack for the ShieldWise gadget and equipment claim-fraud project. It is not the full research dataset. It is a representative sample so my marker, professor, or reviewer can run the project and understand how the modalities connect.

## What Is Included

| Path | Purpose |
| --- | --- |
| `claims/claim_email_ham_spam_sample.csv` | Text/email modality for claim-language risk. |
| `claims/claim_history_sample.csv` | Tabular policy, device, behaviour, evidence, and risk-score fields. |
| `evidence/receipts/` | Small synthetic receipt images for valid, duplicate, cropped, and suspicious document cases. |
| `evidence/repair_quotes/` | A small synthetic repair quote PDF. |
| `evidence/ids/` | A synthetic ID-style image for the identity-evidence workflow. |
| `manifests/evidence_manifest_sample.csv` | Evidence file paths, labels, hashes, and claim links. |
| `manifests/multimodal_sample_index.csv` | Main index linking text, tabular rows, evidence paths, and risk scores. |

## Why This Exists

The full data used during development is too large for normal GitHub storage and may include external dataset licensing constraints. This sample pack keeps the repository runnable and understandable without committing large raw image collections or notebook-only research assets.

The sample covers:

- Normal gadget claims with valid receipts
- Genuine urgent claims
- Claims with missing or partial evidence
- Duplicate receipt scenarios
- Cropped or low-detail receipt scenarios
- Synthetic ID/evidence checks
- Subtle suspicious claim-language examples
- High-risk bank-change and payout-pressure examples

## Regenerate

From the repository root:

```bash
python scripts/prepare_sample_multimodal_data.py
```

The generator writes the same folder structure under `data/sample/`.

## Suggested Reviewer Flow

1. Open `manifests/multimodal_sample_index.csv`.
2. Pick a `claim_id`.
3. Read its email text in `claims/claim_email_ham_spam_sample.csv`.
4. Compare its behavioural/tabular fields in `claims/claim_history_sample.csv`.
5. Open the linked evidence file from `evidence_path`.
6. Compare the three risk components:
   - `email_language_risk_score`
   - `behavioural_risk_score`
   - `document_risk_score`

This demonstrates how ShieldWise combines NLP, structured claim history, and document evidence into one claim-review workflow.
