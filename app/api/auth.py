"""
Authentication API v2 - NAVER OAuth
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from app.db.database import get_db
from app.models.user import User, LoginProvider
from app.core.oauth import NaverOAuth
from app.core.security import create_tokens, verify_token, generate_state_token
from app.core.redis import set_token, get_token, delete_token
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.services.user_service import UserService
from app.schemas.common import CommonResponse, ErrorResponse


router = APIRouter()


# Request models
class NaverLoginRequest(BaseModel):
    """NAVER OAuth login request"""
    code: str = Field(..., example="test_code_123")
    state: str = Field(..., example="test_state_456")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "test_code_123",
                "state": "test_state_456"
            }
        }


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refreshToken: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


# Response data models
class LoginData(BaseModel):
    """Login response data"""
    userId: int
    email: str
    profileImg: Optional[str]
    accessToken: str


class TokenData(BaseModel):
    """Token refresh response data"""
    accessToken: str
    refreshToken: str


@router.post("/naver/login", summary="NAVER Login", description="NAVER OAuth login (Development mode with dummy data)")
async def naver_login(
    request: NaverLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    네이버 OAuth 로그인 엔드포인트
    
    개발 환경에서는 실제 NAVER OAuth 대신 더미 데이터를 사용합니다.
    어떤 code/state가 와도 성공적인 로그인 응답을 반환합니다.
    """
    
    try:
        # 개발용 더미 사용자 데이터 (고정된 하나의 데이터)
        user_profile = {
            "id": "naver_test_user",
            "email": "test@naver.com",
            "nickname": "테스트유저",
            "name": "김테스트",
            "profile_image": "https://ssl.pstatic.net/static/pwe/address/img_profile.png"
        }
        
        # Extract user info
        naver_id = user_profile.get("id")
        email = user_profile.get("email") 
        nickname = user_profile.get("nickname")
        profile_image = user_profile.get("profile_image")
        full_name = user_profile.get("name")
        
        # Check if user exists
        user_service = UserService(db)
        user = await user_service.get_user_by_email(email)
        
        if not user:
            # Create new user
            user = User(
                email=email,
                username=nickname,
                full_name=full_name,
                hashed_password=None,  # OAuth users don't have password
                provider=LoginProvider.NAVER,
                provider_id=naver_id,
                profile_image=profile_image
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            # Update existing user
            if user.provider != LoginProvider.NAVER:
                # Link NAVER account
                user.provider = LoginProvider.NAVER
                user.provider_id = naver_id
            
            if profile_image:
                user.profile_image = profile_image
            
            await db.commit()
            await db.refresh(user)
        
        # Generate JWT tokens
        tokens = create_tokens(user.id)
        
        # Store refresh token in Redis (7 days expiry)
        await set_token(
            f"refresh_token:{tokens['refresh_token']}", 
            {"user_id": user.id},
            expiry=7 * 24 * 3600
        )
        
        # Return response matching the specification
        return CommonResponse.success(data={
            "userId": user.id,
            "email": user.email,
            "profileImg": user.profile_image,
            "accessToken": tokens["access_token"]
        })
        
    except Exception as e:
        return CommonResponse.fail(code="AUTH_001", message=f"로그인 처리 실패: {str(e)}")


@router.post("/reissue/token", summary="Refresh Token", description="Refresh access token using refresh token")
async def refresh_token(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    리프레시 토큰을 사용하여 액세스 토큰 재발급
    
    1. 리프레시 토큰 검증
    2. Redis에서 토큰 존재 확인
    3. 새로운 토큰 생성
    4. Redis에 리프레시 토큰 업데이트
    """
    
    try:
        # Verify refresh token
        payload = verify_token(request.refreshToken, token_type="refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다."
            )
        
        # Check if token exists in Redis
        token_data = await get_token(f"refresh_token:{request.refreshToken}")
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다."
            )
        
        user_id = token_data.get("user_id")
        
        # Check if user exists
        user_service = UserService(db)
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 사용자를 찾을 수 없습니다."
            )
        
        # Delete old refresh token
        await delete_token(f"refresh_token:{request.refreshToken}")
        
        # Generate new tokens
        new_tokens = create_tokens(user_id)
        
        # Store new refresh token in Redis
        await set_token(
            f"refresh_token:{new_tokens['refresh_token']}", 
            {"user_id": user_id},
            expiry=7 * 24 * 3600
        )
        
        return CommonResponse.success(data={
            "accessToken": new_tokens["access_token"],
            "refreshToken": new_tokens["refresh_token"]
        })
        
    except HTTPException as e:
        error_detail = e.detail
        error_code = None
        
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            if "유효하지 않은" in error_detail:
                error_code = "AUTH_001"
            elif "만료" in error_detail:
                error_code = "AUTH_002"
        elif e.status_code == status.HTTP_404_NOT_FOUND:
            error_code = "AUTH_004"
        
        return CommonResponse.fail(code=error_code or "AUTH_001", message=error_detail)
    except Exception as e:
        return CommonResponse.fail(code="COMMON_001", message="서버 내부 오류입니다.")


@router.post("/logout", summary="Logout", description="User logout")
async def logout(
    current_user: User = Depends(get_current_user),
    authorization: str = None
):
    """
    로그아웃 엔드포인트
    
    1. 토큰에서 현재 사용자 확인
    2. Redis에서 리프레시 토큰 삭제
    3. 성공 응답 반환
    """
    
    try:
        # Extract token from authorization header if provided
        if authorization and authorization.startswith("Bearer "):
            access_token = authorization.replace("Bearer ", "")
            
            # Verify access token
            payload = verify_token(access_token, token_type="access")
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않은 토큰입니다."
                )
        
        # Note: We can't delete the access token as it's stateless (JWT)
        # But we can delete associated refresh tokens if needed
        
        # For now, just return success
        # In production, you might want to maintain a blacklist of logged out tokens
        
        return CommonResponse.success(data=None)
        
    except HTTPException as e:
        error_detail = e.detail
        error_code = None
        
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            if "유효하지 않은" in error_detail:
                error_code = "AUTH_001"
            elif "만료" in error_detail:
                error_code = "AUTH_002"
        elif e.status_code == status.HTTP_403_FORBIDDEN:
            error_code = "AUTH_003"
        elif e.status_code == status.HTTP_404_NOT_FOUND:
            error_code = "AUTH_004"
        
        return CommonResponse.fail(code=error_code or "AUTH_001", message=error_detail)
    except Exception as e:
        return CommonResponse.fail(code="COMMON_001", message="서버 내부 오류입니다.")


@router.get("/naver/authorize")
async def get_naver_auth_url():
    """
    Get NAVER OAuth authorization URL
    
    This endpoint generates the URL to redirect users for NAVER login
    """
    oauth_client = NaverOAuth()
    state = generate_state_token()
    
    # Store state in Redis for validation (expires in 10 minutes)
    await set_token(f"oauth_state:{state}", {"valid": True}, expiry=600)
    
    auth_url = oauth_client.get_authorization_url(state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }