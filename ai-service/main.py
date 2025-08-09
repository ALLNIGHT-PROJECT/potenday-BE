"""
AI Task Manager - Multi-agent task management system
PostgreSQL-based with LangChain integration
"""
import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# LangChain imports for multi-agent system
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    AI_ENABLED = True
    logger.info("✅ AI features enabled")
except ImportError:
    AI_ENABLED = False
    logger.warning("⚠️ AI features disabled - install langchain-openai to enable")

# ==================== Database Setup ====================
Base = declarative_base()

# Create database engine with NCloud PostgreSQL support
try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=settings.DB_POOL_PRE_PING,
        echo=settings.DB_ECHO
    )
    # Test connection
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    logger.info("✅ Database connected successfully")
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")
    logger.info("""
    Please check your database configuration:
    1. Ensure DATABASE_URL is correctly set in .env file
    2. For NCloud PostgreSQL, verify security group settings
    3. Check if the database server is accessible from this host
    """)
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== Database Models ====================
class TaskModel(Base):
    """Task database model"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="TODO")
    priority = Column(String(20), default="MEDIUM")
    category = Column(String(50))
    estimated_time = Column(Integer)  # in minutes
    confidence_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    ai_extracted = Column(Boolean, default=False)
    source_text = Column(Text)
    subtasks = Column(Text)  # JSON string
    analysis = Column(Text)  # JSON string

# Create tables
Base.metadata.create_all(bind=engine)

# ==================== Pydantic Models ====================
class TaskCreate(BaseModel):
    """Request model for creating a task"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH)$")
    category: Optional[str] = Field(default=None, max_length=50)


class TaskResponse(BaseModel):
    """Response model for task data"""
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    category: Optional[str]
    estimated_time: Optional[int]
    confidence_score: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    ai_extracted: bool
    subtasks: Optional[List[str]] = None
    analysis: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ExtractRequest(BaseModel):
    """Request model for extracting tasks from text"""
    text: str = Field(..., min_length=1)
    workflow_type: str = Field(
        default="full",
        pattern="^(full|extract_only|analyze_only)$",
        description="Workflow type: full (all agents), extract_only, or analyze_only"
    )


class ProcessRequest(BaseModel):
    """Request model for processing existing tasks"""
    task_id: int = Field(..., gt=0)
    action: str = Field(
        ..., 
        pattern="^(analyze|prioritize|decompose)$",
        description="Action to perform on the task"
    )


# ==================== Multi-Agent System ====================
class MultiAgentProcessor:
    """Multi-agent task processing system"""
    
    def __init__(self):
        """Initialize LLM for agent processing"""
        self.llm = None
        if AI_ENABLED:
            api_key = settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY
            if api_key:
                try:
                    if settings.OPENROUTER_API_KEY:
                        self.llm = ChatOpenAI(
                            model=settings.OPENROUTER_MODEL,
                            temperature=settings.OPENROUTER_TEMPERATURE,
                            api_key=settings.OPENROUTER_API_KEY,
                            base_url=settings.OPENROUTER_BASE_URL
                        )
                    else:
                        self.llm = ChatOpenAI(
                            model="gpt-4o-mini",
                            temperature=0.3,
                            api_key=settings.OPENAI_API_KEY
                        )
                    logger.info("✅ AI agent system initialized")
                except Exception as e:
                    logger.error(f"⚠️ AI initialization failed: {e}")
    
    def extract_agent(self, text: str) -> List[Dict]:
        """Extract tasks from text using AI"""
        if not self.llm:
            return self._fallback_extraction(text)
        
        prompt = """You are a task extraction expert.
Extract actionable tasks from the given text.

Return each task in this format:
{
    "title": "Task title",
    "description": "Detailed description",
    "category": "Development/Meeting/Documentation/Other",
    "priority": "HIGH/MEDIUM/LOW",
    "estimated_time": estimated time in minutes
}

Return as a JSON array."""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=prompt),
                HumanMessage(content=text)
            ])
            
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            
            tasks = json.loads(content)
            return tasks if isinstance(tasks, list) else [tasks]
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return self._fallback_extraction(text)
    
    def analyze_agent(self, task: Dict) -> Dict:
        """Analyze task complexity and dependencies"""
        if not self.llm:
            return {
                "complexity": "MEDIUM",
                "dependencies": [],
                "risks": [],
                "required_skills": []
            }
        
        prompt = f"""Analyze this task:
Title: {task.get('title')}
Description: {task.get('description')}

Return JSON with:
- complexity: LOW/MEDIUM/HIGH
- dependencies: list of dependencies
- risks: potential risks
- required_skills: required skills"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            return json.loads(content)
        except:
            return {"complexity": "MEDIUM", "dependencies": [], "risks": [], "required_skills": []}
    
    def prioritize_agent(self, tasks: List[Dict]) -> List[Dict]:
        """Prioritize tasks based on importance and urgency"""
        if not self.llm or not tasks:
            return tasks
        
        prompt = f"""Prioritize these tasks:
{json.dumps(tasks, ensure_ascii=False, indent=2)}

Consider urgency, importance, and dependencies.
Add priority_score (1-10) to each task and sort by priority."""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            prioritized = json.loads(content)
            return prioritized if isinstance(prioritized, list) else tasks
        except:
            return tasks
    
    def decompose_agent(self, task: Dict) -> List[str]:
        """Decompose task into subtasks"""
        if not self.llm:
            return []
        
        prompt = f"""Break down this task into smaller steps:
{json.dumps(task, ensure_ascii=False, indent=2)}

Each step should be independently executable.
Return as a JSON array of strings."""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            subtasks = json.loads(content)
            return subtasks if isinstance(subtasks, list) else []
        except:
            return []
    
    def _fallback_extraction(self, text: str) -> List[Dict]:
        """Rule-based extraction (fallback when AI is unavailable)"""
        tasks = []
        keywords = {
            "meeting": ("Meeting preparation", "Meeting"),
            "report": ("Report writing", "Documentation"),
            "develop": ("Development task", "Development"),
            "code": ("Code writing", "Development"),
            "review": ("Review task", "Development"),
            "test": ("Testing", "Development"),
            "deploy": ("Deployment", "Development")
        }
        
        text_lower = text.lower()
        for key, (title, category) in keywords.items():
            if key in text_lower:
                tasks.append({
                    "title": title,
                    "description": f"{key} related task",
                    "category": category,
                    "priority": "MEDIUM",
                    "estimated_time": 60
                })
        
        if not tasks:
            tasks.append({
                "title": "Review required",
                "description": text[:200],
                "category": "Other",
                "priority": "LOW",
                "estimated_time": 30
            })
        
        return tasks
    
    def process_workflow(self, text: str, workflow_type: str = "full") -> Dict:
        """Execute complete multi-agent workflow"""
        results = {
            "extracted_tasks": [],
            "analysis": {},
            "prioritization": [],
            "decomposition": {}
        }
        
        # 1. Extract tasks
        extracted = self.extract_agent(text)
        results["extracted_tasks"] = extracted
        
        if workflow_type == "extract_only":
            return results
        
        # 2. Analyze top 3 tasks
        for task in extracted[:3]:
            analysis = self.analyze_agent(task)
            results["analysis"][task["title"]] = analysis
        
        if workflow_type == "analyze_only":
            return results
        
        # 3. Prioritize tasks
        prioritized = self.prioritize_agent(extracted)
        results["prioritization"] = prioritized
        
        # 4. Decompose top priority task
        if prioritized:
            top_task = prioritized[0]
            subtasks = self.decompose_agent(top_task)
            results["decomposition"] = {
                "task": top_task["title"],
                "subtasks": subtasks
            }
        
        return results

# ==================== FastAPI Application ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    app.state.agent_processor = MultiAgentProcessor()
    yield
    logger.info("👋 Shutting down gracefully")

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Helper Functions ====================
def format_task_response(task: TaskModel) -> Dict:
    """Format task model for API response"""
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "category": task.category,
        "estimated_time": task.estimated_time,
        "confidence_score": task.confidence_score,
        "created_at": task.created_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "ai_extracted": task.ai_extracted,
        "subtasks": json.loads(task.subtasks) if task.subtasks else None,
        "analysis": json.loads(task.analysis) if task.analysis else None
    }

# ==================== API Endpoints ====================
@app.get("/")
def root():
    """System information and health check"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "ai_enabled": AI_ENABLED and hasattr(app.state, 'agent_processor') and app.state.agent_processor.llm is not None,
        "database": "PostgreSQL (NCloud ready)",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "extract": "POST /api/extract",
            "tasks": "GET /api/tasks",
            "task": "GET /api/task/{id}",
            "create": "POST /api/task",
            "complete": "PUT /api/task/{id}/complete",
            "delete": "DELETE /api/task/{id}",
            "process": "POST /api/process"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check database
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    ai_status = AI_ENABLED and hasattr(app.state, 'agent_processor') and app.state.agent_processor.llm is not None
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "ai_enabled": ai_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/extract")
async def extract_tasks(request: ExtractRequest, db: Session = Depends(get_db)):
    """
    Extract tasks from text using multi-agent workflow
    
    Workflow types:
    - full: Complete workflow (extract → analyze → prioritize → decompose)
    - extract_only: Only extraction
    - analyze_only: Extract + analyze
    """
    # Execute multi-agent workflow
    results = app.state.agent_processor.process_workflow(request.text, request.workflow_type)
    
    # Save to database
    saved_tasks = []
    for task_data in results["extracted_tasks"]:
        task = TaskModel(
            title=task_data.get("title"),
            description=task_data.get("description"),
            priority=task_data.get("priority", "MEDIUM"),
            category=task_data.get("category"),
            estimated_time=task_data.get("estimated_time"),
            confidence_score=0.85 if app.state.agent_processor.llm else 0.5,
            ai_extracted=bool(app.state.agent_processor.llm),
            source_text=request.text[:500]
        )
        
        # Save analysis results
        if task_data.get("title") in results.get("analysis", {}):
            task.analysis = json.dumps(results["analysis"][task_data["title"]], ensure_ascii=False)
        
        # Save subtasks
        if results.get("decomposition") and task_data.get("title") == results["decomposition"].get("task"):
            task.subtasks = json.dumps(results["decomposition"]["subtasks"], ensure_ascii=False)
        
        db.add(task)
        saved_tasks.append(task)
    
    db.commit()
    
    return {
        "success": True,
        "workflow_type": request.workflow_type,
        "extracted_count": len(saved_tasks),
        "tasks": [format_task_response(t) for t in saved_tasks],
        "analysis": results.get("analysis"),
        "prioritization": results.get("prioritization")
    }

@app.get("/api/tasks")
async def get_tasks(
    status: Optional[str] = Query(None, pattern="^(TODO|IN_PROGRESS|COMPLETED|CANCELLED)$"),
    priority: Optional[str] = Query(None, pattern="^(LOW|MEDIUM|HIGH)$"),
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get task list with filtering"""
    query = db.query(TaskModel)
    
    if status:
        query = query.filter(TaskModel.status == status)
    if priority:
        query = query.filter(TaskModel.priority == priority)
    if category:
        query = query.filter(TaskModel.category == category)
    
    total = query.count()
    tasks = query.order_by(TaskModel.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "count": len(tasks),
        "offset": offset,
        "limit": limit,
        "tasks": [format_task_response(t) for t in tasks]
    }

@app.get("/api/task/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get specific task details"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return format_task_response(task)

@app.post("/api/task")
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create task manually"""
    new_task = TaskModel(
        title=task.title,
        description=task.description,
        priority=task.priority,
        category=task.category,
        ai_extracted=False,
        confidence_score=1.0  # Manual tasks have full confidence
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return {
        "success": True,
        "task": format_task_response(new_task)
    }

@app.put("/api/task/{task_id}/complete")
async def complete_task(task_id: int, db: Session = Depends(get_db)):
    """Mark task as completed"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "COMPLETED"
    task.completed_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Task completed successfully"}

@app.delete("/api/task/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete task"""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"success": True, "message": "Task deleted successfully"}

@app.post("/api/process")
async def process_task(request: ProcessRequest, db: Session = Depends(get_db)):
    """
    Process existing task with additional AI analysis
    
    Actions:
    - analyze: Analyze task complexity
    - prioritize: Re-prioritize with other tasks
    - decompose: Create subtasks
    """
    task = db.query(TaskModel).filter(TaskModel.id == request.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_dict = {
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "category": task.category
    }
    
    result = {}
    
    if request.action == "analyze":
        result = app.state.agent_processor.analyze_agent(task_dict)
        task.analysis = json.dumps(result, ensure_ascii=False)
        
    elif request.action == "prioritize":
        # Re-prioritize with other TODO tasks
        all_tasks = db.query(TaskModel).filter(TaskModel.status == "TODO").limit(10).all()
        tasks_list = [
            {"title": t.title, "priority": t.priority, "id": t.id} 
            for t in all_tasks
        ]
        prioritized = app.state.agent_processor.prioritize_agent(tasks_list)
        result = {"new_priorities": prioritized}
        
    elif request.action == "decompose":
        subtasks = app.state.agent_processor.decompose_agent(task_dict)
        task.subtasks = json.dumps(subtasks, ensure_ascii=False)
        result = {"subtasks": subtasks}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    db.commit()
    
    return {
        "task_id": request.task_id,
        "action": request.action,
        "result": result
    }

# ==================== Main Entry Point ====================
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"""
    ╔══════════════════════════════════════════════════════╗
    ║          {settings.APP_NAME} v{settings.APP_VERSION}                       ║
    ║         Multi-agent Task Management System           ║
    ╚══════════════════════════════════════════════════════╝
    
    🌐 Server: http://localhost:{settings.PORT}
    📚 API Docs: http://localhost:{settings.PORT}/docs
    📖 ReDoc: http://localhost:{settings.PORT}/redoc
    🤖 AI Status: {'Enabled' if AI_ENABLED else 'Disabled'}
    💾 Database: PostgreSQL (NCloud ready)
    
    Multi-agent Workflow:
    1. Extract Agent: Text → Tasks
    2. Analyze Agent: Complexity analysis
    3. Prioritize Agent: Priority sorting
    4. Decompose Agent: Subtask generation
    """)
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )