# HTTPS 설정 가이드

## 개발 환경 (자체 서명 인증서)

### 1. HTTPS 서버 시작
```bash
# 방법 1: 스크립트 사용
./start_https.sh

# 방법 2: 직접 실행
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8443 --ssl-keyfile=ssl/key.pem --ssl-certfile=ssl/cert.pem
```

### 2. API 접근
- HTTPS URL: `https://localhost:8443`
- 자체 서명 인증서 사용 시 브라우저 경고 무시 필요
- curl 사용 시 `-k` 옵션 추가

## 프로덕션 환경 (실제 SSL 인증서)

### 1. Let's Encrypt 인증서 설치 (권장)
```bash
# Certbot 설치
sudo apt-get install certbot

# 인증서 발급 (도메인 필요)
sudo certbot certonly --standalone -d api.potenday.com

# 인증서는 /etc/letsencrypt/live/api.potenday.com/ 에 저장됨
```

### 2. 인증서 복사
```bash
# SSL 디렉토리에 인증서 복사
sudo cp /etc/letsencrypt/live/api.potenday.com/privkey.pem ssl/
sudo cp /etc/letsencrypt/live/api.potenday.com/fullchain.pem ssl/
sudo chown $USER:$USER ssl/*.pem
```

### 3. 프로덕션 서버 시작
```bash
# 포트 443 사용 (sudo 필요)
sudo ./start_production.sh
```

## 보안 고려사항

### 1. 환경 변수 설정
`.env` 파일에 다음 설정 추가:
```env
# SSL/TLS 설정
SSL_KEYFILE=ssl/privkey.pem
SSL_CERTFILE=ssl/fullchain.pem
HTTPS_PORT=443
```

### 2. HTTP → HTTPS 리다이렉션
프로덕션에서는 HTTP 요청을 HTTPS로 자동 리다이렉션:
```python
# app/main.py에 추가 가능
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 3. HSTS (HTTP Strict Transport Security)
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["api.potenday.com", "*.potenday.com"]
)
```

## 테스트

### HTTPS 연결 테스트
```bash
# 자체 서명 인증서 사용 시
curl -k https://localhost:8443/health

# 실제 인증서 사용 시
curl https://api.potenday.com/health
```

### OAuth 로그인 테스트
```bash
curl -k -X POST https://localhost:8443/v1/auth/naver/login \
  -H "Content-Type: application/json" \
  -d '{
    "code": "test_code",
    "state": "test_state"
  }'
```

## 포트 정보
- 개발: HTTPS 8443
- 프로덕션: HTTPS 443 (표준 HTTPS 포트)

## 트러블슈팅

### 1. 포트 권한 오류
```bash
# 1024 이하 포트는 root 권한 필요
sudo python3 -m uvicorn app.main:app --port 443 ...

# 또는 포트 포워딩 사용
sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8443
```

### 2. 인증서 갱신
```bash
# Let's Encrypt 인증서는 90일마다 갱신 필요
sudo certbot renew

# 자동 갱신 설정
sudo crontab -e
# 추가: 0 0 1 * * certbot renew --quiet && systemctl reload nginx
```