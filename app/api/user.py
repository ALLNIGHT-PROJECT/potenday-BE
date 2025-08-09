from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
import asyncio
import json

from app.db.database import get_db
from app.models.user import User
from app.models.user_analysis import UserAnalysis
from app.schemas.common import CommonResponse
from app.core.dependencies import get_current_user
from app.core.ai.user_analyzer import UserProfileAnalyzer


class ProfileUpdateRequest(BaseModel):
    userName: str = Field(..., description="사용자 이름", example="김동현")
    introduction: str = Field(..., max_length=500, description="500자 이내의 자기소개", example="AI와 생산성 툴을 만드는 개발자입니다. 효율적인 워크플로우 자동화와 사용자 경험 개선에 관심이 많으며, 최신 기술 트렌드를 학습하고 적용하는 것을 즐깁니다.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "userName": "김동현",
                "introduction": "AI와 생산성 툴을 만드는 개발자입니다. 효율적인 워크플로우 자동화와 사용자 경험 개선에 관심이 많으며, 최신 기술 트렌드를 학습하고 적용하는 것을 즐깁니다."
            }
        }


router = APIRouter()


async def analyze_user_profile_background(
    user_id: int,
    user_name: str,
    introduction: str,
    db_session: AsyncSession,
    api_key: str = None
):
    """Background task to analyze user profile with AI"""
    try:
        import os
        # Get API key from environment if not provided
        if not api_key:
            api_key = os.getenv("HYPERCLOVA_API_KEY")
        
        analyzer = UserProfileAnalyzer(api_key=api_key)
        
        # Perform AI analysis - returns JSON string
        analysis_json = await analyzer.analyze_user_profile(user_name, introduction)
        
        # Check if analysis already exists
        existing_query = select(UserAnalysis).where(UserAnalysis.user_id == user_id)
        existing_result = await db_session.execute(existing_query)
        existing_analysis = existing_result.scalar_one_or_none()
        
        if existing_analysis:
            # Update existing analysis
            existing_analysis.analysis_data = analysis_json
        else:
            # Create new analysis
            user_analysis = UserAnalysis(
                user_id=user_id,
                analysis_data=analysis_json
            )
            db_session.add(user_analysis)
        
        await db_session.commit()
        print(f"User analysis completed for user {user_id}")
        print(f"Analysis result: {analysis_json}")
        
    except Exception as e:
        print(f"Error analyzing user profile: {str(e)}")
        await db_session.rollback()
    finally:
        await db_session.close()


@router.post("/profile", summary="Update Profile", description="Update user profile and trigger AI analysis")
async def update_user_profile(
    request: ProfileUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 프로필 정보 업데이트 및 AI 분석
    
    사용자의 이름과 자기소개를 업데이트하고,
    백그라운드에서 AI가 사용자 프로필을 분석합니다.
    """
    try:
        # Update user profile
        current_user.full_name = request.userName
        current_user.bio = request.introduction
        
        # Save to database
        await db.commit()
        await db.refresh(current_user)
        
        # Trigger AI analysis in background
        # Create a new session for background task
        from app.db.database import AsyncSessionLocal
        background_db = AsyncSessionLocal()
        
        import os
        api_key = os.getenv("HYPERCLOVA_API_KEY")
        
        background_tasks.add_task(
            analyze_user_profile_background,
            current_user.id,
            request.userName,
            request.introduction,
            background_db,
            api_key
        )
        
        return CommonResponse.success(
            data={
                "message": "프로필이 업데이트되었습니다. AI 분석이 진행 중입니다.",
                "analysis_status": "processing"
            }
        )
        
    except Exception as e:
        await db.rollback()
        return CommonResponse.fail(code="USER_001", message=f"프로필 업데이트 실패: {str(e)}")


@router.get("/analysis", summary="Get User Analysis", description="Get AI-generated user analysis")
async def get_user_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 AI 분석 결과 조회
    
    AI가 분석한 사용자 프로필 정보를 반환합니다.
    """
    try:
        # Get user analysis
        query = select(UserAnalysis).where(UserAnalysis.user_id == current_user.id)
        result = await db.execute(query)
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            return CommonResponse.success(
                data={
                    "status": "not_analyzed",
                    "message": "아직 분석이 완료되지 않았습니다."
                }
            )
        
        # Parse JSON string to dict
        try:
            analysis_dict = json.loads(analysis.analysis_data)
        except:
            analysis_dict = {"error": "Invalid JSON data"}
        
        return CommonResponse.success(
            data={
                "status": "completed",
                "analysis": analysis_dict,
                "analyzed_at": analysis.created_at.isoformat() if analysis.created_at else None
            }
        )
        
    except Exception as e:
        return CommonResponse.fail(code="USER_002", message=f"분석 결과 조회 실패: {str(e)}")