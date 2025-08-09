# Potenday Backend API

AI 기반 업무 관리 서비스 백엔드 API

## 🚀 기술 스택

- **Framework**: FastAPI (Python 3.12)
- **Database**: SQLite (개발) / PostgreSQL (프로덕션)
- **AI**: NAVER HyperCLOVA X
  - HCX-007: 추론 모델 (업무 추출)
  - HCX-005: 빠른 모델 (JSON 검증)
- **Authentication**: JWT Token
- **Type Safety**: Pydantic
- **ORM**: SQLAlchemy (Async)

## 📁 프로젝트 구조

```
potenday-BE/
├── app/
│   ├── api/           # API 엔드포인트
│   ├── core/          # 핵심 기능 (보안, 설정)
│   │   └── ai/        # AI 멀티에이전트 시스템
│   ├── db/            # 데이터베이스 설정
│   ├── models/        # SQLAlchemy 모델
│   ├── schemas/       # Pydantic 스키마
│   ├── services/      # 비즈니스 로직
│   └── main.py        # 애플리케이션 진입점
├── ssl/               # SSL 인증서 (HTTPS)
├── requirements.txt   # Python 의존성
├── init_db.py        # DB 초기화 스크립트
└── .env.example      # 환경 변수 예시
```

## 🛠️ 설치 및 실행

### 사전 요구사항

- Python 3.12+
- SQLite (개발) / PostgreSQL (프로덕션)

### 설치

1. 저장소 클론:
```bash
git clone https://github.com/ALLNIGHT-PROJECT/potenday-BE.git
cd potenday-BE
```

2. 가상 환경 생성:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정:
```bash
cp .env.example .env
# .env 파일 수정
```

5. 데이터베이스 초기화:
```bash
python init_db.py
```

6. 서버 실행:

개발 모드 (HTTP):
```bash
./start_dev.sh
# 또는
uvicorn app.main:app --reload --port 8000
```

프로덕션 모드 (HTTPS):
```bash
./start_production.sh
```

## 📚 API 문서

서버 실행 후 접속:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔧 주요 API 엔드포인트

### 업무 관리 (Tasks)
- `POST /v1/task/extract` - AI 업무 추출
- `POST /v1/task/manual` - 수동 업무 생성
- `GET /v1/task/` - 업무 목록 조회
- `DELETE /v1/task/reset` - 업무 초기화

### 사용자 관리 (User)
- `GET /v1/user/profile` - 프로필 조회
- `PUT /v1/user/profile` - 프로필 수정

## 🤖 멀티에이전트 시스템

### TaskExtractor
- HCX-007 모델 사용
- 텍스트에서 업무 자동 추출
- 사용자 프로필 기반 개인화

### JsonValidatorAgent  
- HCX-005 모델 사용
- JSON 응답 검증 및 수정
- 구조화된 데이터 보장

### UserAnalyzer
- 사용자 행동 분석
- 프로필 기반 업무 추천

## 📝 License

Private - All Rights Reserved