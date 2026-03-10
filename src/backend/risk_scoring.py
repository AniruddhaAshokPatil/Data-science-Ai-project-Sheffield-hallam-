def combined_risk(
    xgb_prob: float | None = None,
    anomaly_score: float | None = None,
    text_score: float | None = None,
    doc_score: float | None = None,
) -> float:
    """
    Beginner-friendly heuristic risk combiner.
    If a component is missing (None), it contributes 0.
    """
    # Simple weights (sum <= 1.0)
    w_tab = 0.6
    w_anom = 0.2
    w_txt = 0.1
    w_doc = 0.1

    val = 0.0
    if xgb_prob is not None:
        val += w_tab * float(xgb_prob)
    if anomaly_score is not None:
        # If your anomaly score is negative/positive, normalise quickly
        # Here we clamp to [0, 1] in a very basic way for a demo
        s = max(0.0, min(1.0, float(anomaly_score)))
        val += w_anom * s
    if text_score is not None:
        val
        