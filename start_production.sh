#!/bin/bash

# Production HTTPS 서버 시작 스크립트

echo "🚀 Starting Potenday Backend Production Server..."

# 환경 변수 설정
export PYTHONPATH=/root/potenday-BE:$PYTHONPATH

# SSL 인증서 경로 (Let's Encrypt 사용 시)
SSL_KEY="ssl/privkey.pem"
SSL_CERT="ssl/fullchain.pem"

# 자체 서명 인증서 fallback
if [ ! -f "$SSL_KEY" ] || [ ! -f "$SSL_CERT" ]; then
    echo "⚠️  Production SSL certificates not found. Using self-signed certificates..."
    SSL_KEY="ssl/key.pem"
    SSL_CERT="ssl/cert.pem"
    
    if [ ! -f "$SSL_KEY" ] || [ ! -f "$SSL_CERT" ]; then
        echo "Generating self-signed certificates..."
        mkdir -p ssl
        openssl req -x509 -newkey rsa:4096 -keyout $SSL_KEY -out $SSL_CERT -days 365 -nodes \
            -subj "/C=KR/ST=Seoul/L=Seoul/O=Potenday/OU=Production/CN=api.potenday.com"
        echo "✅ SSL certificates generated"
    fi
fi

# Production 서버 시작 (workers 수는 CPU 코어 수에 따라 조정)
echo "🔒 Starting Production HTTPS server on port 443..."
sudo python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 443 \
    --ssl-keyfile=$SSL_KEY \
    --ssl-certfile=$SSL_CERT \
    --workers 4 \
    --log-level warning \
    --access-log \
    --use-colors