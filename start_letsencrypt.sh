#!/bin/bash

# Let's Encrypt 인증서로 HTTPS 서버 시작

echo "🔒 Starting HTTPS server with Let's Encrypt certificate..."

# Let's Encrypt 인증서 경로
SSL_KEY="ssl/privkey.pem"
SSL_CERT="ssl/fullchain.pem"

# 인증서 확인
if [ ! -f "$SSL_KEY" ] || [ ! -f "$SSL_CERT" ]; then
    echo "⚠️  Let's Encrypt certificates not found in ssl/ directory"
    echo "Copying from /etc/letsencrypt..."
    
    if [ -f "/etc/letsencrypt/live/223-130-151-253.sslip.io/privkey.pem" ]; then
        sudo cp /etc/letsencrypt/live/223-130-151-253.sslip.io/privkey.pem ssl/
        sudo cp /etc/letsencrypt/live/223-130-151-253.sslip.io/fullchain.pem ssl/
        sudo chown $USER:$USER ssl/*.pem
        echo "✅ Certificates copied"
    else
        echo "❌ Let's Encrypt certificates not found. Run certbot first."
        exit 1
    fi
fi

# HTTPS 서버 시작
echo "🚀 Starting server on https://223-130-151-253.sslip.io:8443"
python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8443 \
    --ssl-keyfile=$SSL_KEY \
    --ssl-certfile=$SSL_CERT \
    --reload \
    --log-level info