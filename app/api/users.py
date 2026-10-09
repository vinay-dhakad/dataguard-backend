from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import User, Event, Alert, Role, Permission, FileRecord
from app.schemas import UserCreate, UserUpdate, PermissionUpdate

router = APIRouter(prefix="/api/users", tags=["Users"])

def serialize_user(u):
    return {"id": u.id, "name": u.name, "email": u.email, "department": u.department,
            "role": u.role.name if u.role else None, "role_id": u.role_id, "is_active": bool(u.is_active)}

def get_user_or_404(db, user_id):
    u = db.query(User).filter(User.id == user_id).first()
    if not u: raise HTTPException(404, "User not found")
    return u

def get_or_create_role(db, name):
    name = name.strip()
    role = db.query(Role).filter(Role.name.ilike(name)).first()
    if not role:
        role = Role(name=name)
        db.add(role); db.flush()
    return role

@router.get("")
def users(db: Session = Depends(get_db)):
    return [serialize_user(u) for u in db.query(User).order_by(User.name).all()]

@router.post("", status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if db.query(User).filter(User.email.ilike(email)).first():
        raise HTTPException(409, "A user with this email already exists")
    role = get_or_create_role(db, data.role)
    user = User(name=data.name.strip(), email=email, department=data.department.strip(), role=role, is_active=data.is_active)
    db.add(user)
    try:
        db.commit(); db.refresh(user)
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "Could not create user; check duplicate fields")
    return serialize_user(user)

@router.get("/{user_id}")
def user(user_id: int, db: Session = Depends(get_db)):
    return serialize_user(get_user_or_404(db, user_id))

@router.patch("/{user_id}")
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    u = get_user_or_404(db, user_id)
    changes = data.model_dump(exclude_unset=True)
    if "email" in changes and changes["email"]:
        email = changes["email"].strip().lower()
        existing = db.query(User).filter(User.email.ilike(email), User.id != user_id).first()
        if existing: raise HTTPException(409, "A user with this email already exists")
        changes["email"] = email
    if "role" in changes:
        role = get_or_create_role(db, changes.pop("role"))
        u.role = role
    for key, value in changes.items():
        if value is not None: setattr(u, key, value.strip() if isinstance(value, str) else value)
    db.commit(); db.refresh(u)
    return serialize_user(u)

@router.get("/{user_id}/activity")
def activity(user_id: int, db: Session = Depends(get_db)):
    get_user_or_404(db, user_id)
    events = db.query(Event).filter(Event.user_id == user_id).order_by(Event.timestamp.desc()).limit(100).all()
    return [{"id": e.id, "file_id": e.file_id, "file_name": e.file.name if e.file else None,
        "action": e.action, "destination": e.destination, "timestamp": e.timestamp,
        "risk_score": e.risk_score, "severity": e.severity, "is_suspicious": e.is_suspicious,
        "permission_allowed": e.permission_allowed, "anomaly_score": e.anomaly_score} for e in events]

@router.get("/{user_id}/risk")
def risk(user_id: int, db: Session = Depends(get_db)):
    u = get_user_or_404(db, user_id)
    events = db.query(Event).filter(Event.user_id == user_id).all()
    alerts = db.query(Alert).filter(Alert.user_id == user_id).all()
    return {"user_id": user_id, "user_name": u.name, "total_events": len(events), "total_alerts": len(alerts),
        "critical_alerts": sum(a.severity == "CRITICAL" for a in alerts), "high_alerts": sum(a.severity == "HIGH" for a in alerts),
        "average_risk_score": round(sum(e.risk_score for e in events)/len(events), 2) if events else 0,
        "max_risk_score": max((e.risk_score for e in events), default=0)}

@router.get("/{user_id}/permissions")
def user_permissions(user_id: int, db: Session = Depends(get_db)):
    get_user_or_404(db, user_id)
    permissions = db.query(Permission).filter(Permission.user_id == user_id).all()
    return [{"user_id": p.user_id, "file_id": p.file_id, "can_read": p.can_read,
             "can_download": p.can_download, "can_share": p.can_share, "can_copy": p.can_copy} for p in permissions]

@router.put("/{user_id}/permissions/{file_id}")
def assign_file_permissions(user_id: int, file_id: int, data: PermissionUpdate, db: Session = Depends(get_db)):
    get_user_or_404(db, user_id)
    if not db.query(FileRecord).filter(FileRecord.id == file_id).first(): raise HTTPException(404, "File not found")
    permission = db.query(Permission).filter(Permission.user_id == user_id, Permission.file_id == file_id).first()
    if not permission:
        permission = Permission(user_id=user_id, file_id=file_id)
        db.add(permission)
    for field, value in data.model_dump().items(): setattr(permission, field, value)
    db.commit(); db.refresh(permission)
    return {"message": "File permissions saved", "user_id": user_id, "file_id": file_id,
            "can_read": permission.can_read, "can_download": permission.can_download,
            "can_share": permission.can_share, "can_copy": permission.can_copy}

@router.delete("/{user_id}/permissions/{file_id}")
def revoke_file_permissions(user_id: int, file_id: int, db: Session = Depends(get_db)):
    get_user_or_404(db, user_id)
    permission = db.query(Permission).filter(Permission.user_id == user_id, Permission.file_id == file_id).first()
    if not permission: raise HTTPException(404, "Permission assignment not found")
    db.delete(permission); db.commit()
    return {"message": "Permission assignment revoked", "user_id": user_id, "file_id": file_id}
