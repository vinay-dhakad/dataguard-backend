from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ExceptionApproval, User, FileRecord
from app.schemas import ExceptionCreate

router = APIRouter(prefix="/api/exceptions", tags=["Exceptions"])

@router.get("")
def get_exceptions(db: Session = Depends(get_db)):
    items = db.query(ExceptionApproval).order_by(ExceptionApproval.created_at.desc()).all()
    return [{
        "id": x.id, "user_id": x.user_id, "user_name": x.user.name if x.user else None,
        "file_id": x.file_id, "file_name": x.file.name if x.file else None,
        "reason": x.reason, "approved_by": x.approved_by,
        "expires_at": x.expires_at, "created_at": x.created_at
    } for x in items]

@router.post("")
def create_exception(data: ExceptionCreate, db: Session = Depends(get_db)):
    if not db.query(User).filter(User.id == data.user_id).first():
        raise HTTPException(404, "User not found")
    if not db.query(FileRecord).filter(FileRecord.id == data.file_id).first():
        raise HTTPException(404, "File not found")
    x = ExceptionApproval(user_id=data.user_id, file_id=data.file_id,
                          reason=data.reason, approved_by=data.approved_by,
                          expires_at=data.expires_at)
    db.add(x); db.commit(); db.refresh(x)
    return {"id": x.id, "message": "Exception approved successfully"}

@router.delete("/{exception_id}")
def delete_exception(exception_id: int, db: Session = Depends(get_db)):
    x = db.query(ExceptionApproval).filter(ExceptionApproval.id == exception_id).first()
    if not x: raise HTTPException(404, "Exception not found")
    db.delete(x); db.commit()
    return {"message": "Exception removed successfully"}
