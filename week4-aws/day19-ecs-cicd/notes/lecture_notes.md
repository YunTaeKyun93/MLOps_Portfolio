# Day 19 강의 노트

**주제**: AWS ECS Fargate 배포 + GitHub Actions → ECR CI/CD
**날짜**: 2026.03.04

---

## 1. ECR (Elastic Container Registry)

### 핵심 개념

- AWS의 Docker 이미지 저장소
- Docker Hub의 AWS 버전
- 이미지 태그 정책: **Mutable** (덮어쓰기 가능) vs **Immutable** (덮어쓰기 불가)

### 백엔드 연결

```
Docker Hub     = npm public registry
ECR            = AWS 전용 private npm registry
이미지 태그     = npm 패키지 버전 (1.0.0, latest)
Immutable tag  = npm에서 이미 배포된 버전 덮어쓰기 금지
```

### 이미지 태깅 전략

```bash
# sha 기반 태깅 (권장)
docker tag app:latest {ECR_URI}/app:{git_sha}

# latest 태깅 (Mutable일 때만 가능)
docker tag app:latest {ECR_URI}/app:latest
```

---

## 2. ECS (Elastic Container Service)

### 핵심 개념

- AWS에서 컨테이너를 실행/관리하는 서비스
- K8s의 AWS 관리형 버전

### 구성 요소 관계

```
ECS Cluster
    └── Service (몇 개의 Task를 항상 유지할지 관리)
            └── Task (실제 실행되는 컨테이너 인스턴스)
                    └── Task Definition (컨테이너 설정 템플릿)
```

### 백엔드 연결

```
ECS Cluster      = K8s Cluster
Service          = K8s Deployment (replica 유지)
Task             = K8s Pod (실제 실행 단위)
Task Definition  = K8s deployment.yaml 템플릿
Fargate          = Vercel/Railway 같은 서버리스 PaaS (EC2 직접 관리 불필요)
```

### Fargate vs EC2

| 구분        | Fargate           | EC2                |
| ----------- | ----------------- | ------------------ |
| 서버 관리   | 불필요            | 직접 관리          |
| 비용        | 실행 시간만 과금  | 인스턴스 항상 과금 |
| 설정        | 간단              | 복잡               |
| 적합한 경우 | 포트폴리오/소규모 | 대규모/비용 최적화 |

---

## 3. 플랫폼 호환성 (M1/M2 Mac)

### 문제

```
Mac M1/M2 = ARM 아키텍처
AWS ECS   = linux/amd64 아키텍처
→ ARM으로 빌드한 이미지는 ECS에서 실행 불가
```

### 해결

```bash
# 크로스 컴파일 (ARM → amd64)
docker build --platform linux/amd64 -t app .
```

### 백엔드 연결

```
Node.js로 치면 Windows에서 빌드한 바이너리를
Linux 서버에서 실행하려는 것과 같은 상황
```

---

## 4. os.path.dirname 경로 계산

### 개념

```python
__file__ = /project/app/services/recommend.py

os.path.abspath(__file__)
# = /project/app/services/recommend.py

os.path.dirname(abspath)         # 1번 = /project/app/services
os.path.dirname(dirname 1번)     # 2번 = /project/app
os.path.dirname(dirname 2번)     # 3번 = /project  ← 루트
```

### 백엔드 연결

```typescript
// NestJS에서 동일한 개념
path.join(__dirname, "../../"); // 2번 올라가기
path.join(__dirname, "../../../"); // 3번 올라가기
```

---

## 5. GitHub Actions Status Check

### 개념

- Branch Protection Rule에서 **Required status checks** 설정
- CI job 이름 = Status check 이름 (정확히 일치해야 함!)

### 주의사항

```yaml
# ci.yml에서 job 이름 바꾸면
jobs:
  test-and-deploy: # ← 이름 변경


# Branch Protection의 Required check도 같이 바꿔야 함
# "test" → "test-and-deploy"
```

---

## 6. IAM (Identity and Access Management)

### 개념

- AWS 리소스 접근 권한 관리
- GitHub Actions에서 AWS 접근할 때 필요

### CI/CD에서 필요한 권한

```
AmazonEC2ContainerRegistryFullAccess  # ECR 푸시/풀
AmazonECS_FullAccess                  # ECS 배포 (선택)
```

### 보안 원칙

```
✅ 필요한 권한만 부여 (최소 권한 원칙)
✅ Access Key는 절대 코드에 하드코딩 금지
✅ GitHub Secrets에 저장
❌ AdministratorAccess는 프로덕션에서 사용 금지
```

---

## 💬 오늘 한 줄 요약

> Mac M1에서 linux/amd64로 크로스 컴파일하고, ECS Fargate에 배포 + GitHub Actions → ECR 자동 푸시 CI/CD 완성
