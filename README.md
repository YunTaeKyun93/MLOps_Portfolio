# MLOps Portfolio

> Nest.js 백엔드 개발 경험을 바탕으로 ML 서빙/배포 역량을 갖춘 백엔드 개발자로 성장하는 12주 기록

---

## 목표

| 항목   | 내용                                          |
| ------ | --------------------------------------------- |
| 포지션 | AI 스타트업 백엔드 개발자 (ML 서빙 경험 보유) |
| 기간   | 12주 (2026.02.06 ~ 2026.05.03)                |
| 전략   | 백엔드 40% + 인프라 40% + ML 기초 20%         |
| 현재   | Nest.js 백엔드, JavaScript 풀스택             |

### 핵심 방향

```
❌ "신입 MLOps 엔지니어"로 지원
✅ "백엔드 개발자 + ML 서빙 경험"으로 지원
✅ 입사 후 ML 서빙 담당 → 1-2년 후 MLOps 전환
```

---

## 진행 상황

### 전체 진행률

```
Phase 1 (Week 1-2):  기본기 + 서빙   ████░░░░░░  40%  ← 진행 중
Phase 2 (Week 3-4):  인프라          ░░░░░░░░░░   0%
Phase 3 (Week 5-8):  MLOps 심화      ░░░░░░░░░░   0%
Phase 4 (Week 9-12): 취업 준비       ░░░░░░░░░░   0%
```

### Week 2 상세

| Day    | 주제                     | 상태    |
| ------ | ------------------------ | ------- |
| Day 6  | BentoML 모델 서빙        | ✅ 완료 |
| Day 7  | CF 추천 시스템 + BentoML | ✅ 완료 |
| Day 8  | FastAPI 서빙 + Docker    | ✅ 완료 |
| Day 9  | MLOps 전체 그림          | ⏳ 예정 |
| Day 10 | Docker 최적화            | ⏳ 예정 |

---

## 로드맵

### Phase 1: 기본기 + 서빙 (Week 1-2) ✅ 진행 중

- ✅ Python + ML 기초 (Week 1)
- ✅ Docker + BentoML (Day 5-6)
- ✅ CF 추천 시스템 (Day 7)
- ✅ FastAPI 서빙 (Day 8)

### Phase 2: 인프라 & K8s (Week 3-4)

- Kubernetes 배포
- CI/CD 파이프라인 (GitHub Actions)
- AWS 클라우드 배포

### Phase 3: MLOps 심화 (Week 5-8)

- Airflow 데이터 파이프라인
- MLflow 모델 관리
- 모니터링 (Prometheus + Grafana)
- 금융 이상 탐지 프로젝트

### Phase 4: 취업 준비 (Week 9-12)

- 포트폴리오 3개 완성
- 이력서 + 포트폴리오 사이트
- 면접 준비 + 지원

---

## 주요 산출물

### ✅ Week 1: Python + ML 기초

```
산출물: best_model.pkl (Titanic 생존 예측 모델)
기술: Python, PyTorch, scikit-learn, pandas
```

### ✅ Week 2: 서빙 + Docker

**Day 7: CF 추천 시스템**

```
산출물:
- train.py (CF 알고리즘 학습)
- service.py (BentoML API)
- user_item_matrix.pkl, user_similarity.pkl

기술: Collaborative Filtering, BentoML, pickle
성능: Accuracy 38.2% (랜덤 대비 2배)
```

**Day 8: FastAPI + Docker**

```
산출물:
- service.py (FastAPI 서버)
- Dockerfile
- GET /recommend/{user_id} API

기술: FastAPI, Docker, Uvicorn
핵심: Path/Query Parameter, lifespan, 레이어 캐싱
```

---

## 포트폴리오 (목표)

### 1. 영화 추천 시스템

```
기술: FastAPI + Docker + AWS ECS + GitHub Actions
핵심: CF 알고리즘 → API 서빙 → 자동 배포
기간: Week 2-4
상태: ⏳ 진행 중 (Day 7-8 완료)
```

### 2. ML 자동화 파이프라인

```
기술: Airflow + MLflow + Prometheus + Grafana
핵심: 모델 자동 재학습 + 성능 모니터링
기간: Week 5-6
상태: ⏳ 예정
```

### 3. 금융 이상 탐지 시스템

```
기술: BentoML + GitLab CI/CD + Kubernetes
핵심: 실시간 이상 탐지 API + K8s 배포
기간: Week 7-8
상태: ⏳ 예정
```

---

## 기술 스택

### 현재 보유 (Week 2 기준)

```
Backend  : Nest.js, FastAPI, Python
ML       : scikit-learn, Collaborative Filtering
Container: Docker, BentoML
Tools    : Git, pandas, numpy
```

### 목표 (12주 후)

```
Backend  : Python, FastAPI, Nest.js
ML       : PyTorch, scikit-learn, MLflow, BentoML
Infra    : Docker, Kubernetes, AWS ECS, GCP
CI/CD    : GitHub Actions, GitLab CI/CD
Monitor  : Prometheus, Grafana, CloudWatch
Data     : Airflow, BigQuery, pandas
```

---

## 프로젝트 구조

```
MLOps_Portfolio/
│
├── week1-basics/               # Week 1: 기본기 ✅
│   ├── day1-setup/            # ML 엔지니어 역할, 환경 설정
│   ├── day2-pytorch/          # PyTorch 기초, MNIST
│   ├── day3-data/             # 데이터 전처리
│   ├── day4-modeling/         # 모델 학습 및 평가
│   ├── day5-docker/           # Docker 기초
│   └── day6-bentoml/          # BentoML 서빙
│
├── week2-serving/              # Week 2: 서빙 + Docker ✅
│   ├── day7-cf-recommender/   # CF 추천 시스템
│   ├── day8-fastapi/          # FastAPI + Docker
│   ├── day9-mlops-concept/    # MLOps 전체 그림 (예정)
│   └── day10-optimization/    # Docker 최적화 (예정)
│
├── week3-kubernetes/           # Week 3: K8s (진행)
├── week4-cloud/                # Week 4: AWS (예정)
├── week5-pipeline/             # Week 5: Airflow (예정)
├── week6-mlflow/               # Week 6: MLflow (예정)
├── week7-anomaly/              # Week 7: 이상 탐지 (예정)
└── week8-review/               # Week 8: 복습 (예정)
```

---

## 학습 원칙

```
✅ 실습 위주       이론보다 코드 먼저
✅ 백엔드 중심     ML보다 인프라/배포에 집중
✅ 매일 커밋       기록을 남기는 습관
✅ 세미코딩        절차형 → 함수형 리팩토링

❌ 완벽주의        일단 돌아가게 만들기
❌ ML 심화         수학/통계 깊게 파지 않기 (필요한 것만)
❌ 강의만 듣기     반드시 실습으로 연결
```

---

## 주요 학습 내용

### Week 1: Python + ML 기초

**Day 1-2: 환경 설정 + PyTorch**

- Miniconda, VS Code 설정
- PyTorch 기초 (텐서, DataLoader)
- MNIST 학습

**Day 3: 데이터 전처리**

- pandas 전처리
- Class Imbalance 처리
- One-Hot Encoding

**Day 4: 모델 학습**

- Titanic 데이터 학습
- RandomForest, Logistic Regression
- best_model.pkl 저장

**Day 5: Docker 기초**

- Dockerfile 작성
- 이미지 빌드 & 실행
- 레이어 캐싱 최적화

**Day 6: BentoML 서빙**

- ModelStore 개념
- service.py 작성
- API 서버 실행 (localhost:3000)

### Week 2: FastAPI + Docker

**Day 7: CF 추천 시스템**

- Collaborative Filtering 알고리즘
- User-Item Matrix 생성
- 코사인 유사도 계산
- BentoML API 서빙
- Accuracy: 38.2%

**Ch2 개념 강의:**

- Matrix Factorization
- SVD, ALS
- KNN (벡터 검색 → RAG 연결)
- Neural Collaborative Filtering

**Day 8: FastAPI + Docker**

- BentoML → FastAPI 전환
- Path/Query Parameter
- lifespan (서버 시작 시 모델 로드)
- Dockerfile 레이어 캐싱
- GET /recommend/{user_id} 구현

**MLOps 개념:**

- ML Lifecycle (순환 구조)
- ML System vs MLOps
- 배포 → 모니터링 → 재학습

---

## 백엔드 개발자 관점 연결

| ML 개념                 | 백엔드 개념                 |
| ----------------------- | --------------------------- |
| FastAPI service.py      | NestJS Controller + Service |
| Pydantic BaseModel      | DTO                         |
| lifespan                | onModuleInit()              |
| Path/Query Parameter    | @Param() / @Query()         |
| pickle                  | 모델 직렬화 저장            |
| BentoML Runner          | 모델 실행 엔진              |
| Docker                  | 실행 환경 패키징            |
| User-Item Matrix        | DB JOIN 결과 (Sparse)       |
| Collaborative Filtering | 유사 사용자 기반 추천       |

---

## 커밋 규칙

```
Day X: [작업 내용]

예시:
Day 7: Add CF recommender with BentoML
Day 8: Implement FastAPI service with Docker
Day 8: Add lecture notes for MLOps concepts
```

---

## 링크

- **GitHub**: [YunTaeKyun93](https://github.com/YunTaeKyun93)
- **Portfolio**: 추후 추가
- **Blog**: 추후 추가

---

## 업데이트 로그

| 날짜       | 내용                              |
| ---------- | --------------------------------- |
| 2026.02.06 | 프로젝트 시작                     |
| 2026.02.10 | Day 1-2 완료 (환경 설정, PyTorch) |
| 2026.02.11 | Day 3 완료 (데이터 전처리)        |
| 2026.02.12 | Day 4-5 완료 (모델 학습, Docker)  |
| 2026.02.13 | Day 6 완료 (BentoML 서빙)         |
| 2026.02.16 | Day 7 완료 (CF 추천 시스템)       |
| 2026.02.18 | Day 8 완료 (FastAPI + Docker)     |

---

> "백엔드 + 인프라가 80% 이상 중요합니다. FastAPI로 모델 서빙하고, Docker로 패키징하고, AWS에 배포하고, CI/CD로 자동화하는 경험이 핵심입니다." - 멘토님 조언

---

**Last Updated**: 2026.02.18 | **Current**: Week 2 - Day 8 완료
