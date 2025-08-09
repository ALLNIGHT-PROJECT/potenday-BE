from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class LoginProvider(enum.Enum):
    LOCAL = "LOCAL"
    NAVER = "NAVER"
    GOOGLE = "GOOGLE"
    KAKAO = "KAKAO"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    bio = Column(String(500), nullable=True)  # User introduction (500 chars max)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    provider = Column(Enum(LoginProvider, create_type=False, native_enum=False), default=LoginProvider.LOCAL)
    provider_id = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    todos = relationship("DailyTodo", back_populates="user", cascade="all, delete-orphan")
    task_sources = relationship("TaskSource", back_populates="user", cascade="all, delete-orphan")
    analysis = relationship("UserAnalysis", back_populates="user", uselist=False, cascade="all, delete-orphan")