#!/bin/bash

# 개발 서버 시작 스크립트 (HTTP)

echo "🚀 Starting Potenday Backend Development Server..."

# 개발 서버 시작 (HTTP, 자동 리로드)
echo "📡 Starting HTTP server on http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"

python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info