from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest

def _features(events):
    rows = []
    for e in events:
        sensitive = int(e.file and e.file.classification in {
            "CONFIDENTIAL", "HIGHLY_SENSITIVE", "CRITICAL"
        })
        risky = int((e.destination or "").upper() in {
            "USB", "PERSONAL_CLOUD", "PERSONAL_EMAIL", "EXTERNAL_MESSAGING"
        })
        transfer = int(e.action in {"DOWNLOAD", "UPLOAD", "USB_COPY", "EMAIL_ATTACHMENT"})
        rows.append([transfer, sensitive, risky, e.timestamp.hour])
    return rows

def calculate_anomaly_score(db, user_id, current_event):
    cutoff = datetime.utcnow() - timedelta(days=30)
    history = db.query(type(current_event)).filter(
        type(current_event).user_id == user_id,
        type(current_event).timestamp >= cutoff,
        type(current_event).id != current_event.id
    ).order_by(type(current_event).timestamp.desc()).limit(100).all()

    if len(history) < 8:
        return 0.0

    model = IsolationForest(n_estimators=100, contamination="auto", random_state=42)
    model.fit(np.array(_features(history), dtype=float))
    raw = float(-model.decision_function(
        np.array(_features([current_event]), dtype=float)
    )[0])
    score = 1 / (1 + np.exp(-6 * raw))
    return round(float(score), 3)
