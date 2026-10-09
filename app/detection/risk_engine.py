def calculate_risk(rule_score, anomaly_score, permission_allowed, action):
    score = rule_score + round(anomaly_score * 30)
    if not permission_allowed:
        score += 10
    if action.upper() in {"USB_COPY", "EMAIL_ATTACHMENT", "UPLOAD"}:
        score += 5

    score = min(score, 100)
    if score >= 80:
        severity = "CRITICAL"
    elif score >= 60:
        severity = "HIGH"
    elif score >= 30:
        severity = "MEDIUM"
    else:
        severity = "LOW"
    return score, severity
