# Day 18 실습 노트 - AWS EC2 + ECR + ECS Fargate 배포

**날짜**: 2026.03.02
**목표**: EC2에 Docker 설치 → ECR 이미지 푸시 → ECS Fargate 배포

---

## 실습 1: EC2 인스턴스 생성 + Docker 설치

### 목표

- [x] EC2 인스턴스 생성 (Ubuntu 22.04 t2.micro)
- [x] SSH 접속
- [x] Docker 설치

### EC2 설정

```
AMI: Ubuntu 22.04 LTS
Instance Type: t2.micro (프리티어)
Key Pair: mlops-key.pem
Security Group: SSH(22) 허용
```

### SSH 접속 (Windows)

```bash
# 권한 설정 (Windows)
icacls mlops-key.pem /inheritance:r
icacls mlops-key.pem /grant:r "%username%:R"

# 접속
ssh -i mlops-key.pem ubuntu@54.145.57.244
```

### Docker 설치

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# 재접속 후 확인
docker --version
# Docker version 28.2.2
```

### 백엔드 연결

```
pem 키 = SSH 개인키 (서버 접속용)
icacls = 윈도우에서 파일 권한 설정 (chmod 400과 동일)
```

---

## 실습 2: Docker Hub 이미지 → EC2에서 실행

### 목표

- [x] Docker Hub에서 이미지 pull
- [x] 컨테이너 실행
- [x] 외부에서 API 접근

### 핵심 명령어

```bash
# 이미지 pull
docker pull yuntaekyun/movie-recommend:v1.0

# 컨테이너 실행
docker run -d -p 8000:8000 yuntaekyun/movie-recommend:v1.0

# 실행 확인
docker ps
```

### 보안 그룹 설정

```
Type: Custom TCP
Port: 8000
Source: 0.0.0.0/0
```

### 결과

```
http://54.145.57.244:8000/docs → FastAPI Swagger UI ✅
```

---

## 실습 3: ECR 이미지 푸시

### 목표

- [x] ECR Repository 생성
- [x] 로컬 이미지 태그
- [x] ECR에 푸시

### 핵심 명령어

```bash
# 1. ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
docker login --username AWS \
--password-stdin 947632012584.dkr.ecr.ap-northeast-2.amazonaws.com

# 2. 이미지 태그
docker tag yuntaekyun/movie-recommend:v1.0 \
947632012584.dkr.ecr.ap-northeast-2.amazonaws.com/movie-recommend:v1.0

# 3. ECR 푸시
docker push \
947632012584.dkr.ecr.ap-northeast-2.amazonaws.com/movie-recommend:v1.0
```

### ECR URI 구조

```
947632012584.dkr.ecr.ap-northeast-2.amazonaws.com/movie-recommend:v1.0
     ↑                    ↑                              ↑          ↑
  AWS 계정 ID           리전                        레포 이름     태그
```

---

## 실습 4: ECS Fargate 배포

### 목표

- [x] ECS 클러스터 생성
- [x] Task Definition 생성
- [x] ECS Service 생성
- [x] 외부 접근 확인

### 순서

```
1. ECS → Clusters → Create cluster
   - Cluster name: movie-recommend-cluster
   - Infrastructure: Fargate

2. Task Definitions → Create
   - Family: movie-recommend-task
   - Launch type: Fargate
   - CPU: 0.25 vCPU
   - Memory: 0.5 GB
   - Container:
     - Image: ECR URI
     - Port: 8000

3. Services → Create
   - Launch type: Fargate
   - Task Definition: movie-recommend-task
   - Desired count: 1
   - Public IP: ENABLED
   - Security Group: 8000 포트 오픈
```

### 결과

```
http://<Public-IP>:8000/docs → FastAPI Swagger UI ✅
```

---

## 🔥 트러블슈팅

| 에러                                    | 원인                             | 해결                                   |
| --------------------------------------- | -------------------------------- | -------------------------------------- |
| `WARNING: UNPROTECTED PRIVATE KEY FILE` | pem 파일 권한 너무 열려있음      | `icacls` 로 권한 제한                  |
| 외부 접속 안 됨                         | Security Group 8000 포트 안 열림 | Inbound rule 추가                      |
| ECR 푸시 실패                           | ECR 로그인 안 함                 | `aws ecr get-login-password` 먼저 실행 |

---

## ✅ 오늘 완성한 것

- [x] EC2 + Docker 환경 구축
- [x] Docker Hub → EC2 직접 실행
- [x] ECR 이미지 푸시
- [x] ECS Fargate 배포
- [x] 외부 Public IP 접근 성공
- [x] 실습 후 전체 리소스 삭제 (비용 절약)

---

## 💡 비용 주의사항

```
실습 후 반드시 삭제:
- ECS Service 삭제
- ECS Cluster 삭제
- ECR 이미지 삭제
- EC2 Terminate (Stop 말고 Terminate!)
- NAT Gateway 있으면 반드시 삭제 (비쌈)
```

---

## 📝 회고

- **배운 것**: ECS = AWS 버전 K8s. Fargate로 서버 없이 컨테이너 실행 가능
- **인상 깊었던 것**: EC2 직접 실행 vs Fargate 차이. 서버리스라는 게 실제로 얼마나 편한지 체감
- **주의할 점**: 리소스 삭제 안 하면 비용 발생. 특히 NAT Gateway 조심
- **내일 연결**: GitHub Actions → ECR 자동 푸시 → ECS 자동 배포 (CD 완성)

---

## Git 커밋

```bash
git add .
git commit -m "feat: Day 18 AWS EC2 + ECR + ECS Fargate 배포"
git push origin feat/day18-aws-ecs
```
