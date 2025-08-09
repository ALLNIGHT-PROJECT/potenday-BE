from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class TaskStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Priority(enum.Enum):
    """Task priority levels - matching API spec"""
    URGENT = "URGENT"
    HIGH = "HIGH"
    MID = "MID"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# Keep old name for compatibility
TaskPriority = Priority


class TaskType(enum.Enum):
    PERSONAL = "PERSONAL"
    WORK = "WORK"
    STUDY = "STUDY"
    OTHER = "OTHER"


class TaskSource(Base):
    """Original text source for task extraction"""
    __tablename__ = "task_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="task_sources")
    tasks = relationship("Task", back_populates="source")


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus, create_type=False, native_enum=False), default=TaskStatus.PENDING)
    priority = Column(Enum(Priority, create_type=False, native_enum=False), default=Priority.MID)
    task_type = Column(Enum(TaskType, create_type=False, native_enum=False), default=TaskType.PERSONAL)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("task_sources.id"), nullable=True)
    
    due_date = Column(DateTime(timezone=True), nullable=True)
    reference = Column(String(500))  # Reference URL
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # AI-related fields
    estimated_time = Column(Integer, nullable=True)  # in minutes
    ai_extracted = Column(Boolean, default=False)
    confidence_score = Column(Integer, default=0)  # 0-100
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    source = relationship("TaskSource", back_populates="tasks")
    subtasks = relationship("SubTask", back_populates="task", cascade="all, delete-orphan")
    todos = relationship("DailyTodo", back_populates="task")


class SubTask(Base):
    __tablename__ = "subtasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    estimated_minutes = Column(Integer, default=30)
    order_idx = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="subtasks")
    daily_subtasks = relationship("DailySubTask", back_populates="subtask")


class DailyTodo(Base):
    """Daily todo items (converted from tasks)"""
    __tablename__ = "daily_todos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    title = Column(String(255), nullable=False)
    priority = Column(Enum(Priority, create_type=False, native_enum=False), default=Priority.MID)
    due_date = Column(DateTime(timezone=True))
    order_idx = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    todo_date = Column(DateTime(timezone=True), server_default=func.now())  # The day this todo is for
    
    # Relationships
    user = relationship("User", back_populates="todos")
    task = relationship("Task", back_populates="todos")
    daily_subtasks = relationship("DailySubTask", back_populates="daily_todo", cascade="all, delete-orphan")


class DailySubTask(Base):
    """Daily subtask items"""
    __tablename__ = "daily_subtasks"
    
    id = Column(Integer, primary_key=True, index=True)
    daily_todo_id = Column(Integer, ForeignKey("daily_todos.id"), nullable=False)
    subtask_id = Column(Integer, ForeignKey("subtasks.id"), nullable=True)
    title = Column(String(255), nullable=False)
    estimated_minutes = Column(Integer, default=30)
    is_checked = Column(Boolean, default=False)
    order_idx = Column(Integer, default=0)
    
    # Relationships
    daily_todo = relationship("DailyTodo", back_populates="daily_subtasks")
    subtask = relationship("SubTask", back_populates="daily_subtasks")