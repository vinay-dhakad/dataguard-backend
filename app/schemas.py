from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class EventCreate(BaseModel):
    user_id: int
    file_id: int
    action: str = Field(min_length=2, max_length=50)
    destination: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[dict[str, Any]] = None

class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    file_id: int
    action: str
    destination: Optional[str]
    timestamp: datetime
    permission_allowed: bool
    anomaly_score: float
    risk_score: int
    severity: str
    is_suspicious: bool

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: str = Field(min_length=5, max_length=200)
    department: str = Field(min_length=2, max_length=100)
    role: str = Field(min_length=2, max_length=100)
    is_active: bool = True

class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    email: Optional[str] = Field(default=None, min_length=5, max_length=200)
    department: Optional[str] = Field(default=None, min_length=2, max_length=100)
    role: Optional[str] = Field(default=None, min_length=2, max_length=100)
    is_active: Optional[bool] = None

class PermissionUpdate(BaseModel):
    can_read: bool = False
    can_download: bool = False
    can_share: bool = False
    can_copy: bool = False

class AlertStatusUpdate(BaseModel):
    status: str

class ExceptionCreate(BaseModel):
    user_id: int
    file_id: int
    reason: str
    approved_by: str
    expires_at: Optional[datetime] = None
