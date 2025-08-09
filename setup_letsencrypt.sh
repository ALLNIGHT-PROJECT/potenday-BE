#!/bin/bash

# Let's Encrypt 인증서 발급 스크립트
# 실제 도메인이 있을 때 사용

echo "🔐 Let's Encrypt SSL 인증서 발급 스크립트"
echo "========================================="
echo ""

# 도메인 입력 받기
read -p "도메인 이름을 입력하세요 (예: api.potenday.com): " DOMAIN
read -p "이메일 주소를 입력하세요 (인증서 만료 알림용): " EMAIL

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "❌ 도메인과 이메일은 필수입니다."
    exit 1
fi

# 도메인 유효성 확인
echo "🔍 도메인 확인 중..."
PUBLIC_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)

echo "  - 서버 공인 IP: $PUBLIC_IP"
echo "  - 도메인 IP: $DOMAIN_IP"

if [ "$PUBLIC_IP" != "$DOMAIN_IP" ]; then
    echo "⚠️  경고: 도메인이 현재 서버를 가리키지 않습니다."
    echo "   DNS 설정을 확인해주세요."
    read -p "계속하시겠습니까? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
fi

# 방법 선택
echo ""
echo "인증서 발급 방법을 선택하세요:"
echo "1) Standalone (서버가 80/443 포트 사용 - 권장)"
echo "2) Webroot (기존 웹서버 사용)"
echo "3) DNS Challenge (DNS TXT 레코드 사용)"
read -p "선택 (1-3): " METHOD

case $METHOD in
    1)
        echo "🚀 Standalone 방식으로 인증서 발급..."
        # 기존 서비스 중지
        echo "기존 서비스를 일시 중지합니다..."
        sudo systemctl stop nginx 2>/dev/null
        pkill -f uvicorn 2>/dev/null
        
        # 인증서 발급
        sudo certbot certonly --standalone \
            --non-interactive \
            --agree-tos \
            --email $EMAIL \
            -d $DOMAIN \
            --preferred-challenges http
        ;;
    
    2)
        echo "🚀 Webroot 방식으로 인증서 발급..."
        # 웹루트 디렉토리 생성
        sudo mkdir -p /var/www/certbot
        
        # 인증서 발급
        sudo certbot certonly --webroot \
            --non-interactive \
            --agree-tos \
            --email $EMAIL \
            -d $DOMAIN \
            -w /var/www/certbot
        ;;
    
    3)
        echo "🚀 DNS Challenge 방식으로 인증서 발급..."
        echo "DNS TXT 레코드를 수동으로 추가해야 합니다."
        
        sudo certbot certonly --manual \
            --preferred-challenges dns \
            --email $EMAIL \
            -d $DOMAIN
        ;;
    
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac

# 인증서 확인
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "✅ 인증서 발급 성공!"
    echo ""
    echo "인증서 위치:"
    echo "  - Certificate: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
    echo "  - Private Key: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
    
    # 인증서 복사
    echo ""
    echo "🔄 인증서를 애플리케이션 디렉토리로 복사..."
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/
    sudo chown $USER:$USER ssl/*.pem
    
    echo "✅ 복사 완료!"
    
    # 자동 갱신 설정
    echo ""
    echo "🔄 자동 갱신 설정..."
    (crontab -l 2>/dev/null; echo "0 0,12 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
    
    echo "✅ 자동 갱신 설정 완료 (매일 0시, 12시 확인)"
    
    # 서버 시작 안내
    echo ""
    echo "📌 이제 HTTPS 서버를 시작할 수 있습니다:"
    echo "   ./start_production.sh"
    
else
    echo "❌ 인증서 발급 실패. 위의 오류 메시지를 확인하세요."
    exit 1
fi