#!/bin/bash

# HTTPS 서버 시작 스크립트

echo "🚀 Starting Potenday Backend HTTPS Server..."

# 환경 변수 설정 (필요시)
export PYTHONPATH=/root/potenday-BE:$PYTHONPATH

# SSL 인증서 경로
SSL_KEY="ssl/key.pem"
SSL_CERT="ssl/cert.pem"

# SSL 인증서 확인
if [ ! -f "$SSL_KEY" ] || [ ! -f "$SSL_CERT" ]; then
    echo "⚠️  SSL certificates not found. Generating self-signed certificates..."
    mkdir -p ssl
    openssl req -x509 -newkey rsa:4096 -keyout $SSL_KEY -out $SSL_CERT -days 365 -nodes \
        -subj "/C=KR/ST=Seoul/L=Seoul/O=Potenday/OU=Development/CN=localhost"
    echo "✅ SSL certificates generated"
fi

# HTTPS 서버 시작
echo "🔒 Starting HTTPS server on port 8443..."
python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8443 \
    --ssl-keyfile=$SSL_KEY \
    --ssl-certfile=$SSL_CERT \
    --reload \
    --log-level info