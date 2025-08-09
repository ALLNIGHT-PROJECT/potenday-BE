-- AI Task Manager 데이터베이스 초기화 스크립트

-- 데이터베이스 생성 (이미 존재하지 않는 경우)
-- CREATE DATABASE ai_task_manager;

-- 테이블 삭제 (초기화용)
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;

-- 작업 테이블 생성
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'TODO',
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    category VARCHAR(50),
    estimated_time INTEGER,
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    ai_extracted BOOLEAN DEFAULT FALSE,
    source_text TEXT,
    subtasks TEXT,
    analysis TEXT
);

-- 사용자 프로필 테이블 생성  
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100),
    preferences TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

-- 샘플 데이터 삽입
INSERT INTO tasks (title, description, priority, category, ai_extracted) VALUES
    ('프로젝트 초기 설정', 'PostgreSQL 데이터베이스 설정 및 연결', 'HIGH', '개발', FALSE),
    ('API 문서 작성', 'REST API 엔드포인트 문서화', 'MEDIUM', '문서', FALSE),
    ('멀티에이전트 시스템 테스트', 'AI 에이전트 워크플로우 검증', 'HIGH', '개발', TRUE);

-- 권한 설정
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO CURRENT_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO CURRENT_USER;