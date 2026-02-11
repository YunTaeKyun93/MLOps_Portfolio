# MLOps Portfolio

> Nest.js 백엔드 개발 경험을 바탕으로 ML 서빙/배포 역량을 갖춘 백엔드 개발자로 성장하는 12주 기록

---

## 목표

| 항목   | 내용                                          |
| ------ | --------------------------------------------- |
| 포지션 | AI 스타트업 백엔드 개발자 (ML 서빙 경험 보유) |
| 기간   | 12주 (2026.02.06 ~ 2025.06.08)                |
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
Phase 1 (Week 1-3):  기본기       ██░░░░░░░░  20%  ← 진행 중
Phase 2 (Week 4-6):  인프라       ░░░░░░░░░░   0%
Phase 3 (Week 7-9):  클라우드     ░░░░░░░░░░   0%
Phase 4 (Week 10-12): 취업 준비   ░░░░░░░░░░   0%
```

### Week 1 상세

| Day   | 주제                            | 상태    |
| ----- | ------------------------------- | ------- |
| Day 1 | ML 엔지니어 역할, 환경 설정     | ✅ 완료 |
| Day 2 | PyTorch 기초, MNIST             | ✅ 완료 |
| Day 3 | 학습 데이터 준비, pandas 전처리 | ✅ 완료 |
| Day 4 | 모델 학습 및 평가               | ⏳ 예정 |
| Day 5 | Docker 기초                     | ⏳ 예정 |
| Day 6 | Week 1 프로젝트                 | ⏳ 예정 |

---

## 로드맵

### Phase 1: 기본기 (Week 1-3)

- Python + ML 기초
- Docker + 컨테이너
- FastAPI 모델 서빙 + CI/CD

### Phase 2: 인프라 & 파이프라인 (Week 4-6)

- AWS 클라우드 배포
- Airflow 워크플로우
- MLflow 모델 관리 + 모니터링

### Phase 3: 실전 프로젝트 (Week 7-9)

- 금융 이상 탐지 시스템
- NLP 모델 서빙 (Triton)
- GCP Vertex AI

### Phase 4: 취업 준비 (Week 10-12)

- 포트폴리오 3개 완성
- 이력서 + 포트폴리오 사이트
- 면접 준비 + 지원

---

## 포트폴리오 (목표)

### 1. 영화 추천 시스템

```
기술: FastAPI + Docker + AWS ECS + GitHub Actions + CloudWatch
핵심: 실시간 추천 API 서빙 + 자동 배포 파이프라인
상태: ⏳ Week 2-4 예정
```

### 2. ML 자동화 파이프라인

```
기술: Airflow + MLflow + Prometheus + Grafana
핵심: 모델 자동 재학습 + 성능 모니터링
상태: ⏳ Week 5-6 예정
```

### 3. 금융 이상 탐지 시스템

```
기술: BentoML + GitLab CI/CD + Triton Inference Server
핵심: 실시간 이상 탐지 API + 고성능 서빙
상태: ⏳ Week 7-8 예정
```

---

## 기술 스택

### 현재 보유

```
Backend  : Nest.js, JavaScript, Python (기초)
Container: Docker (학습 중)
Tools    : Git, Linux (기본)
```

### 목표 (12주 후)

```
Backend  : Python, FastAPI, Nest.js
ML       : PyTorch, scikit-learn, MLflow, BentoML
Infra    : Docker, Kubernetes, AWS, GCP
CI/CD    : GitHub Actions, GitLab CI/CD
Monitor  : Prometheus, Grafana
Data     : Airflow, BigQuery, pandas
```

---

## 프로젝트 구조

```
MLOps_Portfolio/
│
├── week1-basics/               # Week 1: 기본기
│   ├── day1-setup/            # ML 엔지니어 역할, 환경 설정
│   ├── day2-pytorch/          # PyTorch 기초, MNIST
│   ├── day3-data/             # 데이터 전처리 ← 완료
│   ├── day4-modeling/         # 모델 학습 및 평가
│   ├── day5-docker/           # Docker 기초
│   └── day6-project/          # Week 1 미니 프로젝트
│
├── week2-serving/              # Week 2: FastAPI 서빙
├── week3-deployment/           # Week 3: K8s + CI/CD
├── week4-cloud/                # Week 4: AWS 배포
├── week5-pipeline/             # Week 5: Airflow
├── week6-mlflow/               # Week 6: MLflow + 모니터링
├── week7-anomaly/              # Week 7: 이상 탐지
├── week8-nlp/                  # Week 8: NLP 서빙
├── week9-review/               # Week 9: 복습 + 보강
│
├── project1-movie-recommend/   # 포트폴리오 1
├── project2-ml-pipeline/       # 포트폴리오 2
└── project3-anomaly-detect/    # 포트폴리오 3
```

---

## 학습 원칙

```
✅ 실습 위주       이론보다 코드 먼저
✅ 백엔드 중심     ML보다 인프라/배포에 집중
✅ 매일 커밋       기록을 남기는 습관
✅ 막히면 질문     혼자 30분 이상 고민하지 않기

❌ 완벽주의        일단 돌아가게 만들기
❌ ML 심화         수학/통계 깊게 파지 않기
❌ 강의만 듣기     반드시 실습으로 연결
```

---

## 일별 학습 기록

### Week 1

**Day 1** - ML 엔지니어 역할, 환경 설정

- [강의] [B] Part 1. Ch 1 (MLOps 개념, 환경 설정)
- [설치] Miniconda, Python 3.11, VS Code, GCP SDK
- [배운 것] MLOps = 재현성 + 상품화, 백엔드 경험이 강점인 이유

**Day 2** - PyTorch 기초

- [강의] [B] Part 1. Ch 2 (PyTorch, MNIST)
- [실습] 텐서 연산, DataLoader, MNIST 학습
- [배운 것] float32 이유, DataLoader num_workers, Prefetching

**Day 3** - 학습 데이터 준비

- [강의] [P] Part 2. Ch 1 (01-02 ~ 01-06)
- [실습] pandas 전처리, Class Imbalance 확인
- [배운 것] Chained Assignment, get_dummies vs OneHotEncoder, bool→int

---

## 커밋 규칙

```
Day X: [작업 내용]

예시:
Day 3: Add data preprocessing script
Day 3: Complete lecture notes on data preparation
Day 3: Add class imbalance visualization
```

---

## 링크

- **GitHub**: [YunTaeKyun93](https://github.com/YunTaeKyun93)
- **Portfolio**: 추후 추가
- **Blog**: 추후 추가

---

## 데이터 준비

예시

```bash
# Kaggle CLI로 다운로드
kaggle competitions download -c titanic
mv titanic.zip week1-basics/day3-data/data/titanic/
unzip week1-basics/day3-data/data/titanic/titanic.zip

___


## 업데이트 로그

| 날짜       | 내용                                        |
| ---------- | ------------------------------------------- |
| 2026.02.09 | 프로젝트 시작                               |
| 2025.02.10 | Day 1-2 완료 (환경 설정, PyTorch 기초)      |
| 2026.02.11 | Day 3 완료 (데이터 전처리, Class Imbalance) |

---

> "백엔드 + 인프라가 80% 이상 중요합니다. FastAPI로 모델 서빙하고, Docker로 패키징하고, AWS에 배포하고, CI/CD로 자동화하는 경험이 핵심입니다." - 멘토님 조언

---

**Last Updated**: 2026.02.11 | **Current**: Week 1 - Day 3 완료
```
