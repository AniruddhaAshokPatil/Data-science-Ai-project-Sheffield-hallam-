def _clamp(value):
    return max(0.0, min(1.0, float(value)))


def combined_risk(
    xgb_prob=None,
    anomaly_score=None,
    text_score=None,
    doc_score=None,
):
    """
    Beginner-friendly heuristic risk combiner.
    If a component is missing (None), it contributes 0.
    """
    w_tab = 0.6
    w_anom = 0.2
    w_txt = 0.1
    w_doc = 0.1

    val = 0.0
    if xgb_prob is not None:
        val += w_tab * _clamp(xgb_prob)
    if anomaly_score is not None:
        val += w_anom * _clamp(anomaly_score)
    if text_score is not None:
        val += w_txt * _clamp(text_score)
    if doc_score is not None:
        val += w_doc * _clamp(doc_score)

    return _clamp(val)
