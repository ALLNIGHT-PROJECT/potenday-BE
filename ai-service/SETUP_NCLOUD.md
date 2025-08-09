# NCloud PostgreSQL 설정 가이드

## 현재 DB 정보
- **DB Service 이름**: acti
- **DB Server 이름**: acti-001-7r05
- **Private 도메인**: pg-36ui97.vpc-cdb-kr.ntruss.com
- **Private IP**: 10.0.1.7
- **Port**: 5432
- **Username**: db
- **Password**: asdf!234
- **DB 엔진**: PostgreSQL 14.18

## ⚠️ 연결 문제 해결

현재 외부에서 직접 연결이 불가능한 상태입니다. 다음 방법 중 하나를 선택하세요:

### 방법 1: Public 도메인 할당 (권장)
1. NCloud Console 접속
2. Cloud DB for PostgreSQL > DB Service 선택
3. 'acti' 서비스 선택
4. Public 도메인 할당
5. ACG(Access Control Group) 설정에서 본인 IP 추가

### 방법 2: SSL VPN 사용
1. NCloud SSL VPN 서비스 생성
2. VPN 클라이언트 설치 및 연결
3. Private 도메인으로 직접 연결

### 방법 3: Bastion Host 사용
1. 같은 VPC 내에 Public IP를 가진 서버 생성
2. SSH 터널링 설정:
```bash
ssh -L 5432:pg-36ui97.vpc-cdb-kr.ntruss.com:5432 user@bastion-host
```

### 방법 4: 애플리케이션 서버에서 실행
NCloud 내부의 서버(같은 VPC)에서 애플리케이션을 실행하면 Private 도메인으로 직접 연결 가능

## ACG (Access Control Group) 설정

현재 ACG: cloud-postgresql-1s9vs5 (293848)

### 규칙 추가 방법:
1. NCloud Console > Server > ACG
2. 'cloud-postgresql-1s9vs5' 선택
3. Inbound 규칙 추가:
   - Protocol: TCP
   - Port: 5432
   - Source: 본인 IP 또는 애플리케이션 서버 IP

## 연결 문자열

### Private 도메인 사용 (VPC 내부):
```
postgresql://db:asdf!234@pg-36ui97.vpc-cdb-kr.ntruss.com:5432/ai_task_manager
```

### Public 도메인 사용 (할당 후):
```
postgresql://db:asdf!234@[public-domain]:5432/ai_task_manager
```

## 데이터베이스 생성

연결 성공 후 다음 SQL 실행:
```sql
-- ai_task_manager 데이터베이스 생성
CREATE DATABASE ai_task_manager;

-- 데이터베이스 전환
\c ai_task_manager;
```

## 보안 권장사항

1. **Production 환경**:
   - SSL 연결 사용: `?sslmode=require` 추가
   - 강력한 비밀번호로 변경
   - IP 화이트리스트 엄격히 관리

2. **개발 환경**:
   - VPN 또는 Bastion Host 사용
   - 임시 Public 도메인 사용 시 사용 후 즉시 제거

## 테스트

연결 설정 완료 후:
```bash
# 연결 테스트
python test_connection.py

# 애플리케이션 실행
python main.py
```