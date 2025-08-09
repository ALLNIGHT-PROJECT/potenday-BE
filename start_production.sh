#!/bin/bash

# 프로덕션 HTTPS 서버 시작 스크립트

echo "🚀 Starting Potenday Backend Production Server..."

# SSL 인증서 경로
SSL_KEY="ssl/privkey.pem"
SSL_CERT="ssl/fullchain.pem"

# SSL 인증서 확인
if [ ! -f "$SSL_KEY" ] || [ ! -f "$SSL_CERT" ]; then
    echo "❌ SSL certificates not found in ssl/ directory"
    echo "Please ensure ssl/privkey.pem and ssl/fullchain.pem exist"
    exit 1
fi

# 프로덕션 서버 시작 (포트 8443 사용)
echo "🔒 Starting Production HTTPS server on port 8443..."
echo "📡 Access: https://your-domain.com:8443"

python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8443 \
    --ssl-keyfile=$SSL_KEY \
    --ssl-certfile=$SSL_CERT \
    --workers 4 \
    --log-level warning \
    --access-log