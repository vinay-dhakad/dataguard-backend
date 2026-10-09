from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventResponse
from app.services.event_service import process_event

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.post("", response_model=EventResponse)
async def create_event(data: EventCreate, db: Session = Depends(get_db)):
    try:
        event, _, _ = await process_event(db, data)
        return event
    except ValueError as e:
        raise HTTPException(404, str(e))

@router.get("", response_model=list[EventResponse])
def get_events(user_id: int | None = Query(None), limit: int = Query(100, le=500), db: Session = Depends(get_db)):
    q = db.query(Event).order_by(Event.timestamp.desc())
    if user_id:
        q = q.filter(Event.user_id == user_id)
    return q.limit(limit).all()
