from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    department = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    role = relationship("Role", back_populates="users")
    events = relationship("Event", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    permissions = relationship("Permission", back_populates="user", cascade="all, delete-orphan")

class FileRecord(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    classification = Column(String(50), nullable=False)
    owner_department = Column(String(100), nullable=False)
    events = relationship("Event", back_populates="file")
    permissions = relationship("Permission", back_populates="file", cascade="all, delete-orphan")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    can_read = Column(Boolean, default=False)
    can_download = Column(Boolean, default=False)
    can_share = Column(Boolean, default=False)
    can_copy = Column(Boolean, default=False)
    user = relationship("User", back_populates="permissions")
    file = relationship("FileRecord", back_populates="permissions")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    action = Column(String(50), nullable=False)
    destination = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    permission_allowed = Column(Boolean, default=True)
    anomaly_score = Column(Float, default=0.0)
    risk_score = Column(Integer, default=0)
    severity = Column(String(20), default="LOW")
    is_suspicious = Column(Boolean, default=False)
    metadata_json = Column(Text)
    user = relationship("User", back_populates="events")
    file = relationship("FileRecord", back_populates="events")
    alert = relationship("Alert", back_populates="event", uselist=False)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    risk_score = Column(Integer, nullable=False)
    severity = Column(String(20), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(30), default="OPEN")
    suggested_response = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime)
    event = relationship("Event", back_populates="alert")
    user = relationship("User", back_populates="alerts")

class ExceptionApproval(Base):
    __tablename__ = "exceptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    reason = Column(String(500), nullable=False)
    approved_by = Column(String(150), nullable=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
