import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert, Event
from app.schemas import AlertStatusUpdate

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

def serialize(db, a):
    e = db.query(Event).filter(Event.id == a.event_id).first()
    try:
        reasons = json.loads(a.reason)
    except Exception:
        reasons = [a.reason]
    return {
        "id": a.id, "event_id": a.event_id, "user_id": a.user_id,
        "user_name": a.user.name if a.user else "Unknown",
        "file_name": e.file.name if e.file else "Unknown",
        "action": e.action, "destination": e.destination,
        "risk_score": a.risk_score, "severity": a.severity,
        "reason": reasons, "status": a.status,
        "suggested_response": a.suggested_response,
        "created_at": a.created_at
    }

@router.get("")
def get_alerts(status=None, severity=None, user_id=None, db: Session = Depends(get_db)):
    q = db.query(Alert).order_by(Alert.created_at.desc())
    if status: q = q.filter(Alert.status == status.upper())
    if severity: q = q.filter(Alert.severity == severity.upper())
    if user_id: q = q.filter(Alert.user_id == int(user_id))
    return [serialize(db, a) for a in q.all()]

@router.get("/{alert_id}")
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a: raise HTTPException(404, "Alert not found")
    return serialize(db, a)

@router.patch("/{alert_id}")
def update_alert(alert_id: int, data: AlertStatusUpdate, db: Session = Depends(get_db)):
    allowed = {"OPEN", "INVESTIGATING", "RESOLVED", "FALSE_POSITIVE", "APPROVED"}
    status = data.status.upper()
    if status not in allowed:
        raise HTTPException(400, "Invalid alert status")
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a: raise HTTPException(404, "Alert not found")
    a.status = status
    if status in {"RESOLVED", "FALSE_POSITIVE", "APPROVED"}:
        a.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(a)
    return serialize(db, a)
