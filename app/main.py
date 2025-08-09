from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import auth, user, tasks
from app.core.config import settings
from app.db.database import engine, Base
# Import all models to ensure they are registered with SQLAlchemy
from app.models import user as user_models, task as task_models
from app.models import user_analysis as user_analysis_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Skip table creation for now
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Potenday Backend API",
    version=settings.VERSION,
    description="AI-powered task management service backend API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/v1/user", tags=["User"])
app.include_router(tasks.router, prefix="/v1/task", tags=["Task"])


@app.get("/")
async def root():
    return {"message": "Potenday Backend API", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}