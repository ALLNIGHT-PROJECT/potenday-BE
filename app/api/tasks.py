"""
Task management API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.user import User
from app.models.task import Task, SubTask, TaskSource, Priority, TaskStatus
from app.core.dependencies import get_current_user
from app.schemas.common import CommonResponse
from app.core.ai.hyperclova import HyperClovaClient
from app.core.ai.task_extractor import TaskExtractor


router = APIRouter()


# Request models
class TaskExtractRequest(BaseModel):
    """Task extraction request"""
    originalText: str = Field(..., example="오늘 회의에서 다음 주까지 프레젠테이션 자료를 준비하고 보고서를 작성해야 한다고 했습니다.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "originalText": "오늘 회의에서 다음 주까지 프레젠테이션 자료를 준비하고 보고서를 작성해야 한다고 했습니다."
            }
        }


class SubTaskRequest(BaseModel):
    """Subtask request model for manual task creation"""
    title: str = Field(..., example="자료 조사하기")
    estimatedMin: int = Field(..., example=60)


class ManualTaskRequest(BaseModel):
    """Manual task creation request"""
    title: str = Field(..., example="프레젠테이션 자료 준비")
    description: Optional[str] = Field(None, example="다음 주 회의를 위한 분기 실적 프레젠테이션 자료 작성")
    priority: str = Field("MID", example="HIGH")
    dueDate: Optional[datetime] = Field(None, example="2024-12-31T23:59:59")
    reference: Optional[str] = Field(None, example="2024년 4분기 실적 회의")
    subTasks: Optional[List[SubTaskRequest]] = Field(None, example=[
        {"title": "자료 조사하기", "estimatedMin": 60},
        {"title": "슬라이드 작성하기", "estimatedMin": 120},
        {"title": "리뷰 및 수정하기", "estimatedMin": 30}
    ])
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "프레젠테이션 자료 준비",
                "description": "다음 주 회의를 위한 분기 실적 프레젠테이션 자료 작성",
                "priority": "HIGH",
                "dueDate": "2024-12-31T23:59:59",
                "reference": "2024년 4분기 실적 회의",
                "subTasks": [
                    {"title": "자료 조사하기", "estimatedMin": 60},
                    {"title": "슬라이드 작성하기", "estimatedMin": 120},
                    {"title": "리뷰 및 수정하기", "estimatedMin": 30}
                ]
            }
        }


# Response models
class SubTaskResponse(BaseModel):
    """Subtask response"""
    title: str
    estimatedMin: int
    isChecked: bool = Field(default=False, description="세부 업무 완료 여부")


class TaskResponse(BaseModel):
    """Task response"""
    title: str
    description: str
    dueDate: Optional[datetime]
    priority: str
    references: str = Field(default="", description="참고 자료 URL")  # 빈 문자열 기본값
    totalEstimatedMin: int = Field(default=0, description="총 예상 시간(분 단위)")
    isCompleted: bool = Field(default=False, description="업무 완료 여부")
    subTasks: List[SubTaskResponse]


@router.post("/extract", summary="Extract Tasks", description="Extract tasks from text using AI")
async def extract_tasks(
    request: TaskExtractRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    자동 업무(Task) 추출 - AI를 통한 자동 추출
    
    제공한 업무소스(Task Source)로부터 자동으로 업무(Task)와 하위의 세부업무(SubTask) 추출
    사용자의 프로필 정보를 활용하여 맞춤형 업무 추출
    """
    try:
        # Save task source
        task_source = TaskSource(
            user_id=current_user.id,
            original_text=request.originalText
        )
        db.add(task_source)
        await db.flush()
        
        # Get user's analyzed profile if exists
        from app.models.user_analysis import UserAnalysis
        import json
        
        user_profile = None
        analysis_query = select(UserAnalysis).where(UserAnalysis.user_id == current_user.id)
        analysis_result = await db.execute(analysis_query)
        user_analysis = analysis_result.scalar_one_or_none()
        
        if user_analysis and user_analysis.analysis_data:
            try:
                user_profile = json.loads(user_analysis.analysis_data)
                print(f"Using user profile for task extraction: {user_profile.get('user_name', 'Unknown')}")
            except:
                pass
        
        # Use TaskExtractor for better extraction with user context
        import os
        # Explicitly set API key - same as background task
        api_key = "nv-be52cfefb87b477b8cb39dc149e7ce96nudW"
        extractor = TaskExtractor(api_key=api_key)
        
        # Extract tasks using AI with user profile
        extracted_tasks = await extractor.extract_tasks(request.originalText, user_profile)
        
        if not extracted_tasks:
            # Fallback if no tasks extracted
            extracted_tasks = [{
                "title": "추출된 업무",
                "description": request.originalText[:500],
                "dueDate": None,
                "priority": "mid",
                "reference": None,
                "subTasks": [
                    {"title": "업무 분석하기", "estimatedMin": 30},
                    {"title": "계획 수립하기", "estimatedMin": 60},
                    {"title": "실행하기", "estimatedMin": 120}
                ]
            }]
        
        created_tasks = []
        
        for task_data in extracted_tasks:
            # Create task in database
            task = Task(
                user_id=current_user.id,
                source_id=task_source.id,
                title=task_data.get("title", "제목 없음"),
                description=task_data.get("description", ""),
                priority=Priority[task_data.get("priority", "mid").upper()],
                due_date=datetime.fromisoformat(task_data["dueDate"]) if task_data.get("dueDate") else None,
                reference=task_data.get("reference"),
                ai_extracted=True,
                confidence_score=90 if len(extracted_tasks) > 0 else 50
            )
            db.add(task)
            await db.flush()
            
            # Create subtasks
            subtasks_response = []
            total_estimated_minutes = 0
            for idx, subtask_data in enumerate(task_data.get("subTasks", [])):
                subtask = SubTask(
                    task_id=task.id,
                    title=subtask_data.get("title", f"세부 업무 {idx+1}"),
                    estimated_minutes=subtask_data.get("estimatedMin", 30),
                    order_idx=idx,
                    is_completed=False  # 명시적으로 False 설정
                )
                db.add(subtask)
                total_estimated_minutes += subtask.estimated_minutes
                subtasks_response.append({
                    "title": subtask.title,
                    "estimatedMin": subtask.estimated_minutes,
                    "isChecked": False  # 항상 False로 반환
                })
            
            # Prepare response data
            created_tasks.append({
                "title": task.title,
                "description": task.description,
                "dueDate": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority.value,
                "references": task.reference or "",  # references로 통일, null이면 빈 문자열 (s 추가)
                "totalEstimatedMin": total_estimated_minutes,  # 분 단위로 반환
                "isCompleted": task.status == TaskStatus.COMPLETED,  # Task의 완료 상태
                "subTasks": subtasks_response
            })
        
        await db.commit()
        
        return CommonResponse.success(data=created_tasks)
        
    except Exception as e:
        await db.rollback()
        print(f"Task extraction error: {str(e)}")
        return CommonResponse.fail(
            code="TASK_001",
            message=f"업무 추출 실패: {str(e)}"
        )


@router.post("/manual", summary="Create Manual Task", description="Create task manually")
async def create_manual_task(
    request: ManualTaskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    수동 업무(Task) 생성 - 사용자가 직접 입력
    subTasks가 제공되면 직접 사용하고, 없으면 AI로 생성
    """
    try:
        # Create task
        task = Task(
            user_id=current_user.id,
            title=request.title,
            description=request.description or "",
            priority=Priority[request.priority.upper()],
            due_date=request.dueDate,
            reference=request.reference,
            ai_extracted=False
        )
        db.add(task)
        await db.flush()
        
        # Check if subTasks are provided in request
        if request.subTasks and len(request.subTasks) > 0:
            # Use provided subTasks
            subtasks_data = [
                {
                    "title": st.title,
                    "estimatedMin": st.estimatedMin
                }
                for st in request.subTasks
            ]
            print(f"Using {len(subtasks_data)} subtasks from request")
        else:
            # Generate subtasks with AI (HCX-005 fast model)
            ai_client = HyperClovaClient(model="HCX-005")
            
            system_prompt = f"""주어진 업무에 대한 세부 업무(SubTask)를 생성해주세요.
            
            업무 정보:
            - 제목: {request.title}
            - 설명: {request.description or '없음'}
            - 우선순위: {request.priority}
            - 마감일: {request.dueDate or '없음'}
            - 참고 링크: {request.reference or '없음'}
            
            3-5개의 세부 업무를 JSON 배열로 반환하세요:
            [{{"title": "세부 업무 제목", "estimatedMin": 예상시간(분)}}]"""
            
            try:
                ai_response = await ai_client.extract_tasks(
                    f"Task: {request.title}\nDescription: {request.description}",
                    system_prompt
                )
                
                import json
                subtasks_data = json.loads(ai_response) if isinstance(ai_response, str) else ai_response
                
                # Ensure it's a list
                if not isinstance(subtasks_data, list):
                    subtasks_data = [subtasks_data]
                
                print(f"AI generated {len(subtasks_data)} subtasks")
                
            except Exception as ai_error:
                print(f"AI subtask generation failed: {ai_error}")
                # Default subtasks based on task type
                if "지원" in request.title or "채용" in request.title:
                    subtasks_data = [
                        {"title": "공고 분석하기 : 필수자격 및 우대 사항 확인", "estimatedMin": 30},
                        {"title": "필수 역량에 적합한 경험 분석하기", "estimatedMin": 60},
                        {"title": "포트폴리오 수정하기", "estimatedMin": 240},
                        {"title": "지원서 작성하기", "estimatedMin": 120}
                    ]
                else:
                    subtasks_data = [
                        {"title": "요구사항 분석하기", "estimatedMin": 30},
                        {"title": "계획 수립하기", "estimatedMin": 60},
                        {"title": "작업 수행하기", "estimatedMin": 120},
                        {"title": "검토 및 마무리", "estimatedMin": 30}
                    ]
        
        # Create subtasks in database
        subtasks_response = []
        total_estimated_minutes = 0
        for idx, subtask_data in enumerate(subtasks_data):
            subtask = SubTask(
                task_id=task.id,
                title=subtask_data.get("title", f"세부 업무 {idx+1}"),
                estimated_minutes=subtask_data.get("estimatedMin", 60),
                order_idx=idx,
                is_completed=False  # 명시적으로 False 설정 (새 업무는 항상 미완료)
            )
            db.add(subtask)
            total_estimated_minutes += subtask.estimated_minutes
            subtasks_response.append({
                "title": subtask.title,
                "estimatedMin": subtask.estimated_minutes,
                "isChecked": False  # 항상 False로 반환 (새 업무는 항상 미완료)
            })
        
        await db.commit()
        await db.refresh(task)
        
        return CommonResponse.success(data={
            "title": task.title,
            "description": task.description,
            "dueDate": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority.value,
            "references": task.reference or "",  # references로 통일, null이면 빈 문자열
            "totalEstimatedMin": total_estimated_minutes,  # 자동 계산된 총 예상 시간
            "isCompleted": False,  # 새 업무는 항상 False
            "subTasks": subtasks_response
        })
        
    except Exception as e:
        await db.rollback()
        return CommonResponse.fail(
            code="TASK_002",
            message=f"업무 생성 실패: {str(e)}"
        )


@router.delete("/reset", summary="Reset All Tasks", description="Delete all tasks for current user")
async def reset_all_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자의 모든 Task 초기화 (삭제)
    모든 Task와 연관된 SubTask, TaskSource도 함께 삭제
    """
    try:
        # Get all tasks for the user
        task_query = select(Task).where(Task.user_id == current_user.id)
        task_result = await db.execute(task_query)
        tasks = task_result.scalars().all()
        
        deleted_count = len(tasks)
        
        # Delete all subtasks for these tasks
        for task in tasks:
            subtask_query = select(SubTask).where(SubTask.task_id == task.id)
            subtask_result = await db.execute(subtask_query)
            subtasks = subtask_result.scalars().all()
            
            for subtask in subtasks:
                await db.delete(subtask)
            
            # Delete the task itself
            await db.delete(task)
        
        # Also delete all task sources for the user
        source_query = select(TaskSource).where(TaskSource.user_id == current_user.id)
        source_result = await db.execute(source_query)
        sources = source_result.scalars().all()
        
        for source in sources:
            await db.delete(source)
        
        await db.commit()
        
        return CommonResponse.success(data={
            "message": f"Successfully deleted {deleted_count} tasks and all related data",
            "deleted_tasks": deleted_count
        })
        
    except Exception as e:
        await db.rollback()
        return CommonResponse.fail(
            code="TASK_004",
            message=f"업무 초기화 실패: {str(e)}"
        )


@router.get("/")
async def get_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자의 모든 Task 조회
    """
    try:
        query = select(Task).where(
            Task.user_id == current_user.id,
            Task.status != TaskStatus.CANCELLED
        ).order_by(Task.created_at.desc())
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        tasks_data = []
        for task in tasks:
            # Get subtasks
            subtasks_query = select(SubTask).where(
                SubTask.task_id == task.id
            ).order_by(SubTask.order_idx)
            
            subtasks_result = await db.execute(subtasks_query)
            subtasks = subtasks_result.scalars().all()
            
            # Calculate total estimated minutes
            total_estimated_minutes = sum(st.estimated_minutes for st in subtasks)
            
            tasks_data.append({
                "title": task.title,
                "description": task.description,
                "dueDate": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority.value,
                "references": task.reference or "",  # references로 통일, null이면 빈 문자열
                "totalEstimatedMin": total_estimated_minutes,
                "isCompleted": task.status == TaskStatus.COMPLETED,
                "subTasks": [
                    {
                        "title": st.title,
                        "estimatedMin": st.estimated_minutes,
                        "isChecked": st.is_completed  # isChecked로 통일
                    }
                    for st in subtasks
                ]
            })
        
        return CommonResponse.success(data=tasks_data)
        
    except Exception as e:
        return CommonResponse.fail(
            code="TASK_003",
            message=f"업무 조회 실패: {str(e)}"
        )