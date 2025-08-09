"""
Configuration settings for AI Task Manager
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8090
    DEBUG: bool = False
    
    # NCloud PostgreSQL Configuration
    # Format: postgresql://username:password@host:port/database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/ai_task_manager"
    )
    
    # Database Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False  # SQL 쿼리 로깅
    
    # OpenRouter LLM Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini"
    OPENROUTER_TEMPERATURE: float = 0.3
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # OpenAI Alternative (if not using OpenRouter)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Application Settings
    APP_NAME: str = "AI Task Manager"
    APP_VERSION: str = "2.0"
    APP_DESCRIPTION: str = "Multi-agent task management system with AI"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()


# NCloud PostgreSQL 연결 정보 예시
"""
NCloud PostgreSQL 설정 방법:

1. NCloud Console에서 Cloud DB for PostgreSQL 생성
2. 접속 정보 확인:
   - Host: xxx.pg.naverncp.com
   - Port: 5432 (기본값)
   - Database: ai_task_manager
   - Username: 설정한 사용자명
   - Password: 설정한 비밀번호

3. .env 파일에 설정:
   DATABASE_URL=postgresql://username:password@xxx.pg.naverncp.com:5432/ai_task_manager

4. 보안 그룹 설정:
   - 애플리케이션 서버의 IP 허용
   - PostgreSQL 포트(5432) 열기

5. SSL 연결 (권장):
   DATABASE_URL에 ?sslmode=require 추가
   예: postgresql://user:pass@host:5432/db?sslmode=require
"""