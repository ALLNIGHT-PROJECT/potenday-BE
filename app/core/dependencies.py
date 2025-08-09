from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.db.database import get_db
from app.models.user import User, LoginProvider
from app.services.user_service import UserService

# Make tokenUrl optional for development
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from token, or return None if no token provided.
    For development mode without authentication.
    """
    if not token:
        # In development mode, create/get a default test user
        user_service = UserService(db)
        test_email = "test@naver.com"
        
        # Try to get existing test user
        user = await user_service.get_user_by_email(test_email)
        
        if not user:
            # Create test user if doesn't exist
            user = User(
                email=test_email,
                username="테스트유저",
                full_name="김테스트",
                hashed_password=None,
                provider=LoginProvider.NAVER,
                provider_id="naver_test_user",
                profile_image="https://ssl.pstatic.net/static/pwe/address/img_profile.png"
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        return user
    
    # If token is provided, verify it
    payload = verify_token(token)
    if payload is None:
        return None
    
    user_id: str = payload.get("sub")
    if user_id is None:
        return None
    
    user_service = UserService(db)
    user = await user_service.get_user(int(user_id))
    
    return user


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """
    Get current user, either from token or default test user.
    Always returns a user (never None).
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user