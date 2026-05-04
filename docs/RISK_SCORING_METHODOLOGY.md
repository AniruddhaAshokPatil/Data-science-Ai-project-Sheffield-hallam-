# ShieldWise Risk Scoring Methodology

This document records the current risk scoring values used by the gadget insurance claim workflow.
The weights are intentionally not equal because each signal has a different level of importance in a high-value device claim.

## Final Risk Formula

```python
total_risk = (email_risk * 0.30) + (behavioural_risk * 0.42) + (document_risk * 0.28)
```

The system gives the largest share to behavioural risk because account changes, repeated claims, new policies, and unusual device-claim patterns can quickly change the overall fraud concern.
Document risk is also weighted strongly because gadget claims depend heavily on receipts, repair invoices, and ID evidence.

## Risk Labels

| Final Score | Label |
| --- | --- |
| `>= 0.65` | High |
| `>= 0.32` | Medium / Review |
| `< 0.32` | Low |

The thresholds are deliberately sensitive so important warning signs move a claim into review quickly.

## Behavioural Risk Weights

Base behavioural risk starts at `0.12`.

| Signal | Exact Risk Added |
| --- | ---: |
| Recent high-value purchase | `+0.12` |
| Unusual spending spike | `+0.13` |
| Login location changed | `+0.11` |
| Multiple devices in 7 days | `+0.10` |
| Address changed recently | `+0.09` |
| Phone changed recently | `+0.08` |
| Bank details changed recently | `+0.16` |
| Late-night submission | `+0.06` |
| Weekend submission | `+0.04` |

## Extra Behavioural Rules

| Signal | Exact Risk Added |
| --- | ---: |
| Each prior claim | `+0.10`, capped at `+0.30` |
| Each claim in last 12 months | `+0.12`, capped at `+0.36` |
| Policy age <= 30 days | `+0.24` |
| Claim amount / device value >= 1.3 | `+0.22` |
| Behavioural risk cap | `0.98` |

## Document / Receipt Risk Weights

Document risk starts from the evidence result.

| Signal | Exact Risk Added |
| --- | ---: |
| Receipt missing | base document risk becomes `0.38` |
| Receipt present | base document risk is usually `0.10` |
| Receipt mismatch | `+0.36` |
| Duplicate receipt | `+0.34` in final document scoring |
| Image tamper suspected | `+0.38` in final document scoring |
| Document risk cap | `0.98` |

## Uploaded Evidence Checker Weights

These checks run before final document scoring.

| Evidence Check | Exact Risk Added |
| --- | ---: |
| Duplicate SHA-256 file match | `+0.34` |
| Image smaller than 300px on shortest side | `+0.24` |
| Image aspect ratio > 4 | `+0.14` |
| Low-colour image mode `1` or `P` | `+0.10` |
| Unreadable/corrupt image | `+0.42` |
| PDF base risk | `+0.10` |
| PDF size < 25 KB | extra `+0.20` |

## Main Code Locations

- `src/api/services/insurance_data.py`
- `src/api/services/document_risk.py`
