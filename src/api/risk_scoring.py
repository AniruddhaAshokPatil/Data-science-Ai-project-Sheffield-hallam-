def _clamp(value):
    # I clamp values here because combined fraud scores should stay between
    # 0 and 1, even if one component gives me an out-of-range number.
    numeric_value = float(value)
    clamped_value = max(0.0, min(1.0, numeric_value))
    return clamped_value


def combined_risk(
    xgb_prob=None,
    anomaly_score=None,
    text_score=None,
    doc_score=None,
):
    """
    I use this function to combine multiple fraud signals into one final
    risk score for the wider project.

    I keep missing components as None because not every request will have
    tabular, anomaly, text, and document evidence at the same time.
    """
    w_tab = 0.6
    w_anom = 0.2
    w_txt = 0.1
    w_doc = 0.1

    # I start from zero and then add only the signals that are available.
    combined_value = 0.0

    if xgb_prob is not None:
        tabular_value = _clamp(xgb_prob)
        combined_value += w_tab * tabular_value

    if anomaly_score is not None:
        anomaly_value = _clamp(anomaly_score)
        combined_value += w_anom * anomaly_value

    if text_score is not None:
        text_value = _clamp(text_score)
        combined_value += w_txt * text_value

    if doc_score is not None:
        document_value = _clamp(doc_score)
        combined_value += w_doc * document_value

    # I clamp the final result again so the returned risk always stays valid.
    final_risk = _clamp(combined_value)
    return final_risk
