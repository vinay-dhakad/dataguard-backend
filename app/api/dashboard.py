from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Event, Alert

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    alerts = db.query(Alert).all()
    return {
        "total_events": len(events),
        "total_alerts": len(alerts),
        "open_alerts": sum(a.status == "OPEN" for a in alerts),
        "critical_alerts": sum(a.severity == "CRITICAL" for a in alerts),
        "high_alerts": sum(a.severity == "HIGH" for a in alerts),
        "medium_alerts": sum(a.severity == "MEDIUM" for a in alerts),
        "suspicious_events": sum(e.is_suspicious for e in events)
    }

@router.get("/risk-trend")
def risk_trend(days: int = 7, db: Session = Depends(get_db)):
    start = datetime.utcnow() - timedelta(days=max(1, min(days, 30)))
    events = db.query(Event).filter(Event.timestamp >= start).order_by(Event.timestamp).all()
    groups = {}
    for e in events:
        day = e.timestamp.strftime("%Y-%m-%d")
        groups.setdefault(day, {"date": day, "events": 0, "risk_total": 0, "max_risk": 0, "alerts": 0})
        groups[day]["events"] += 1
        groups[day]["risk_total"] += e.risk_score
        groups[day]["max_risk"] = max(groups[day]["max_risk"], e.risk_score)
    for a in db.query(Alert).filter(Alert.created_at >= start).all():
        day = a.created_at.strftime("%Y-%m-%d")
        if day in groups: groups[day]["alerts"] += 1
    return [{
        "date": x["date"], "events": x["events"],
        "average_risk": round(x["risk_total"]/x["events"], 2),
        "max_risk": x["max_risk"], "alerts": x["alerts"]
    } for x in groups.values()]

@router.get("/recent-alerts")
def recent_alerts(limit: int = 10, db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(min(limit, 50)).all()
    return [{"id": a.id, "user_id": a.user_id,
             "user_name": a.user.name if a.user else None,
             "risk_score": a.risk_score, "severity": a.severity,
             "status": a.status, "created_at": a.created_at} for a in alerts]
