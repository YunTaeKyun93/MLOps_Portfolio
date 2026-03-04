# Day 19 실습 노트 1 - ECS Fargate 배포

**날짜**: 2026.03.04
**목표**: movie-recommend API를 AWS ECS Fargate에 배포

---

## 실습 순서

### 1. linux/amd64 이미지 빌드

```bash
# M1 Mac에서 amd64용 이미지 빌드
docker build --platform linux/amd64 -t movie-recommend .
```

### 2. ECR 이미지 푸시

```bash
# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin \
  947632012584.dkr.ecr.ap-northeast-2.amazonaws.com

# sha 태깅
GIT_SHA=$(git rev-parse --short HEAD)
docker tag movie-recommend:latest \
  947632012584.dkr.ecr.ap-northeast-2.amazonaws.com/movie-recommend:${GIT_SHA}

# 푸시
docker push \
  947632012584.dkr.ecr.ap-northeast-2.amazonaws.com/movie-recommend:${GIT_SHA}
```

### 3. ECS Task Definition 생성

- 앱 환경: **Fargate**
- 운영체제: **Linux/X86_64**
- 이미지 URL: `947632012584.dkr.ecr.ap-northeast-2.amazonaws.com/movie-recommend:{sha}`
- 포트: `8000`
- CPU: `0.5 vCPU`, 메모리: `1 GB`

### 4. ECS 서비스 생성

- 클러스터: `movie-recommend-cluster`
- Task Definition: `movie-recommend-task_beta:최신버전`
- 원하는 태스크 수: `1`

### 5. 보안 그룹 인바운드 규칙 추가

- 유형: 사용자 지정 TCP
- 포트: `8000`
- 소스: `0.0.0.0/0`

### 6. API 확인

```bash
curl http://{퍼블릭IP}:8000/health
curl http://{퍼블릭IP}:8000/recommend/1
```

---

## AWS 인프라 현황

```
ECR:         947632012584.dkr.ecr.ap-northeast-2.amazonaws.com/movie-recommend
ECS Cluster: movie-recommend-cluster
Task:        movie-recommend-task_beta
리전:         ap-northeast-2 (서울)
```

---

## ✅ 완성한 것

- [x] linux/amd64 이미지 빌드
- [x] ECR 푸시
- [x] ECS Fargate 배포
- [x] 보안 그룹 설정
- [x] API 정상 동작 확인 (`/docs`, `/recommend/1`)

---

## 📝 회고

- 배운 것: ECS 구성 요소 (Cluster → Service → Task → Task Definition)
- 막혔던 부분: M1 플랫폼 이슈, Task Definition inactive, 보안 그룹 미설정
- 내일 연결: GitHub Actions → ECR 자동화
