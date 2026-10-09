from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import FileRecord, Permission

router = APIRouter(prefix="/api/files", tags=["Files"])

@router.get("")
def files(db: Session = Depends(get_db)):
    return [{"id": f.id, "name": f.name, "classification": f.classification,
             "owner_department": f.owner_department,
             "permission_count": db.query(Permission).filter(Permission.file_id == f.id).count()}
            for f in db.query(FileRecord).order_by(FileRecord.name).all()]

@router.get("/{file_id}")
def file(file_id: int, db: Session = Depends(get_db)):
    f = db.query(FileRecord).filter(FileRecord.id == file_id).first()
    if not f: raise HTTPException(404, "File not found")
    ps = db.query(Permission).filter(Permission.file_id == file_id).all()
    return {"id": f.id, "name": f.name, "classification": f.classification,
        "owner_department": f.owner_department,
        "permissions": [{"user_id": p.user_id, "user_name": p.user.name if p.user else None,
            "can_read": p.can_read, "can_download": p.can_download,
            "can_share": p.can_share, "can_copy": p.can_copy} for p in ps]}
