"""
User analysis model for storing AI-generated user insights
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class ExperienceLevel(str, enum.Enum):
    """User experience level"""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class UserAnalysis(Base):
    """AI-generated user analysis data - simplified version"""
    __tablename__ = "user_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Store complete LLM output as JSON string
    analysis_data = Column(Text, nullable=False)  # Complete JSON output from LLM
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analysis")