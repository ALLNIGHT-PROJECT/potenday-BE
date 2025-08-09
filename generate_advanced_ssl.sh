#!/bin/bash

# 고급 자체 서명 SSL 인증서 생성 스크립트
# SAN (Subject Alternative Names) 지원으로 여러 도메인/IP 사용 가능

echo "🔐 고급 SSL 인증서 생성 스크립트"
echo "================================="

# SSL 디렉토리 생성
mkdir -p ssl

# 설정 파일 생성
cat > ssl/openssl.cnf <<EOF
[req]
default_bits = 4096
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=KR
ST=Seoul
L=Seoul
O=Potenday
OU=Development
CN=localhost

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = api.potenday.com
DNS.3 = *.potenday.com
IP.1 = 127.0.0.1
IP.2 = 10.0.1.9
EOF

# 개인키 생성
echo "🔑 개인키 생성 중..."
openssl genpkey -algorithm RSA -out ssl/private.key -pkeyopt rsa_keygen_bits:4096

# CSR (Certificate Signing Request) 생성
echo "📝 CSR 생성 중..."
openssl req -new -key ssl/private.key -out ssl/request.csr -config ssl/openssl.cnf

# 자체 서명 인증서 생성 (1년 유효)
echo "📜 인증서 생성 중..."
openssl x509 -req -days 365 -in ssl/request.csr \
    -signkey ssl/private.key \
    -out ssl/certificate.crt \
    -extensions v3_req \
    -extfile ssl/openssl.cnf

# PEM 형식으로 변환
echo "🔄 PEM 형식으로 변환 중..."
cp ssl/private.key ssl/key.pem
cp ssl/certificate.crt ssl/cert.pem

# 인증서 정보 확인
echo ""
echo "✅ SSL 인증서 생성 완료!"
echo ""
echo "📋 인증서 정보:"
openssl x509 -in ssl/cert.pem -text -noout | grep -A 2 "Subject:\|Subject Alternative Name"

echo ""
echo "📁 생성된 파일:"
echo "  - 개인키: ssl/key.pem"
echo "  - 인증서: ssl/cert.pem"
echo ""
echo "🚀 서버 시작:"
echo "  ./start_https.sh"