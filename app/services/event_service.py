import json
from datetime import datetime
from app.models import User, FileRecord, Event
from app.detection.permission_engine import check_permission
from app.detection.rule_engine import evaluate_rules
from app.detection.anomaly_engine import calculate_anomaly_score
from app.detection.risk_engine import calculate_risk
from app.services.alert_service import create_alert, broadcast_alert

async def process_event(db, data):
    user = db.query(User).filter(User.id == data.user_id).first()
    file = db.query(FileRecord).filter(FileRecord.id == data.file_id).first()
    if not user:
        raise ValueError("User not found")
    if not file:
        raise ValueError("File not found")

    event = Event(
        user_id=user.id, file_id=file.id,
        action=data.action.upper(),
        destination=data.destination,
        timestamp=data.timestamp or datetime.utcnow(),
        metadata_json=json.dumps(data.metadata or {})
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    allowed, permission_reason = check_permission(db, user.id, file.id, event.action)
    rule_score, reasons = evaluate_rules(
        event.action, file.classification, event.destination, allowed
    )
    if permission_reason and permission_reason != "Action is authorized":
        reasons.append(permission_reason)

    anomaly = calculate_anomaly_score(db, user.id, event)
    if anomaly >= 0.60:
        reasons.append(f"Unusual behaviour detected (anomaly score {anomaly:.2f})")

    risk, severity = calculate_risk(rule_score, anomaly, allowed, event.action)

    event.permission_allowed = allowed
    event.anomaly_score = anomaly
    event.risk_score = risk
    event.severity = severity
    event.is_suspicious = risk >= 30
    db.commit()
    db.refresh(event)

    alert = None
    if risk >= 30:
        alert = create_alert(db, event, reasons)
        await broadcast_alert(db, alert)

    return event, alert, reasons
