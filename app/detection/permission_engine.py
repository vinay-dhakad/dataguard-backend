from datetime import datetime
from app.models import ExceptionApproval, Permission, User

# Unknown file operations are denied by default: explicit grants are required.
FIELDS = {
    "FILE_ACCESS": "can_read", "READ": "can_read", "VIEW": "can_read", "PRINT": "can_read",
    "DOWNLOAD": "can_download", "UPLOAD": "can_share", "SHARE": "can_share",
    "EMAIL_ATTACHMENT": "can_share", "CLOUD_UPLOAD": "can_share", "PERSONAL_CLOUD": "can_share",
    "USB_COPY": "can_copy", "CLIPBOARD": "can_copy", "COPY": "can_copy"
}

def check_permission(db, user_id, file_id, action):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return False, "User is missing or inactive"
    now = datetime.utcnow()
    exceptions = db.query(ExceptionApproval).filter(ExceptionApproval.user_id == user_id,
        ExceptionApproval.file_id == file_id).all()
    if any(x.expires_at is None or x.expires_at >= now for x in exceptions):
        return True, "Approved exception applies"
    permission = db.query(Permission).filter(Permission.user_id == user_id,
        Permission.file_id == file_id).first()
    if not permission:
        return False, "No permission record exists for this user and file"
    field = FIELDS.get(action.upper())
    if not field:
        return False, f"No permission rule is defined for action {action}"
    allowed = bool(getattr(permission, field, False))
    return allowed, ("Action is authorized" if allowed else f"User is not authorized to perform {action}")
