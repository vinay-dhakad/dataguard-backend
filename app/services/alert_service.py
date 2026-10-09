import json
from app.models import Alert, Event, User, FileRecord
from app.websocket import manager

def suggested_response(severity):
    if severity == "CRITICAL":
        return "Immediately investigate and consider temporarily blocking the transfer."
    if severity == "HIGH":
        return "Review the file, destination and user timeline."
    if severity == "MEDIUM":
        return "Verify whether the activity is expected."
    return "No immediate action required."

def create_alert(db, event, reasons):
    alert = Alert(
        event_id=event.id,
        user_id=event.user_id,
        risk_score=event.risk_score,
        severity=event.severity,
        reason=json.dumps(reasons),
        status="OPEN",
        suggested_response=suggested_response(event.severity)
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

async def broadcast_alert(db, alert):
    event = db.query(Event).filter(Event.id == alert.event_id).first()
    user = db.query(User).filter(User.id == alert.user_id).first()
    file = db.query(FileRecord).filter(FileRecord.id == event.file_id).first()
    try:
        reasons = json.loads(alert.reason)
    except Exception:
        reasons = [alert.reason]

    await manager.broadcast({
        "type": "NEW_ALERT",
        "alert_id": alert.id,
        "event_id": event.id,
        "user_id": user.id,
        "user_name": user.name,
        "file_name": file.name,
        "action": event.action,
        "destination": event.destination,
        "risk_score": alert.risk_score,
        "severity": alert.severity,
        "reason": reasons,
        "status": alert.status,
        "suggested_response": alert.suggested_response,
        "created_at": alert.created_at.isoformat()
    })
