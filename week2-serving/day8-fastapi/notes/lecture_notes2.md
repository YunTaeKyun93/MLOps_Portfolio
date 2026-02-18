# Day 8 - MLOps 개념 강의노트
> Week 2 | MLOps 서빙/배포 파트  
> 강의: [P] Part2 Ch2-01~03

---

## Ch2-01. ML LifeCycle은 어떻게 구성되어 있는가? (26:49) 🟡

### ML Lifecycle 전체 흐름

```
문제 정의
→ 데이터 준비
→ Feature Engineering
→ 모델 학습
→ 평가
→ 배포
→ 모니터링
→ 재학습 (반복)
```

**핵심:** ML은 한 번 하고 끝이 아니라 **순환 구조**다.

### 1. Data Collection & Preparation

실제로 대부분 시간이 여기서 쓰임.

```
하는 일:
- 문제 정의
- 데이터 수집
- 데이터 정제
- EDA (탐색적 데이터 분석)
```

예: 추천 시스템
```
문제: 영화 추천
데이터: 사용자 평점
EDA: 평점 분포, Sparsity 확인
```

**핵심 포인트:** 모델보다 데이터가 더 중요하다.

### 2. Feature Engineering

모델이 이해할 수 있게 데이터 변환하는 단계.

```
작업:
- Categorical Encoding (원-핫, 라벨)
- Scaling (정규화, 표준화)
- 결측치 처리
- 파생 변수 생성
```

예:
```
나이 → 20대/30대/40대 그룹
평점 → normalized rating (0~1)
```

이 단계가 모델 성능을 크게 좌우한다.

### 3. Model Selection & Training

#### Model Selection
어떤 모델을 쓸지 결정.

```
예:
- Logistic Regression
- Random Forest
- Neural Network
- Collaborative Filtering
```

#### Model Training
Loss를 최소화하면서 학습.

```
지표 예:
- MSE (회귀)
- Cross Entropy (분류)
- RMSE (추천)
```

### 4. Evaluation & Tuning

"이 모델을 믿어도 되나?" 질문에 답하는 단계.

```
작업:
- Validation
- Metric 계산 (Accuracy, F1, RMSE 등)
- Hyperparameter Tuning
```

### 5. Deployment & Monitoring

**MLOps에서 가장 중요한 구간!**

여기서 처음으로 ML이 "서비스"가 된다.

```
배포:
- API 서버로 모델 배포
- DB와 연결
- 사용자 요청 처리

모니터링:
- 모델 성능 추적
- Latency 체크
- Error rate 확인
```

**중요한 점:** 모델 성능은 시간이 지나면 떨어진다. (Data Drift, Concept Drift)

### 6. Re-Evaluation & Model Update

**ML Lifecycle의 핵심 개념!**

```
잘못된 인식:
train → deploy → 끝

올바른 흐름:
train → deploy → monitoring → 성능 저하 → retrain → redeploy
```

ML은 순환 구조다.

---

## Ch2-02. ML System은 무엇인가? (6:53) 🟡

### ML System 정의

```
ML System = 모델을 실제로 사용하게 만드는 시스템

데이터 → 모델 → 예측 → 사용자
```

### ML System 구성 요소

```
1. 데이터 수집 및 처리
2. 모델 개발 및 훈련
3. 추론 (inference)
4. 사용자 인터페이스 / API
```

예: 추천 시스템
```
데이터베이스 (평점)
    ↓
추천 모델 (CF)
    ↓
API 서버 (FastAPI)
    ↓
웹 서비스
```

### ML System vs ML Lifecycle

**강의 핵심 문장:**
> ML System은 ML LifeCycle을 모두 고려하지 않는다.

차이:
```
ML System
- 특정 모델 구현 중심
- 예: 추천 모델 API 서버

ML Lifecycle
- 모델 전체 생명주기
- 예: 데이터 관리, 재학습, 모니터링, 업데이트
```

**관계:**
```
ML System ⊂ ML Lifecycle
```

---

## Ch2-03. MLOps의 등장과 핵심 기능 (37:18) 🟡

### MLOps 정의

```
MLOps = Machine Learning Operations

모델을 구축하고, 배포하고, 관리하기 위한 프로세스
(자동화 중심)
```

**핵심:**
> MLOps는 전체 ML Lifecycle을 통합하는 개념

### MLOps가 등장한 이유

#### 1. 신뢰성 확보

ML 모델은 데이터에 매우 의존함.

```
MLOps 역할:
- 데이터 품질 관리
- 모델 검증
- 모니터링
```

#### 2. 빠른 개발과 배포

CI/CD 기반 자동화.

```
코드 수정
→ 자동 학습
→ 자동 테스트
→ 자동 배포
```

#### 3. 재현성 확보

버전 관리가 핵심.

```
관리 대상:
- 데이터 버전
- 모델 버전
- 코드 버전
```

#### 4. 비용 절감

자동화로 시간과 인력 절약.

### MLOps 핵심 기능

#### 1. 데이터 관리
```
- 데이터 수집
- 저장
- 전처리
- 버전 관리 (DVC)
```

#### 2. 모델 개발 및 훈련
```
- 실험 관리 (MLflow)
- 모델 선택
- Hyperparameter Tuning
```

#### 3. 모델 배포 및 서빙
```
- Docker
- Kubernetes
- REST API (FastAPI, BentoML)
```

#### 4. 모니터링
```
- 정확도 변화 추적
- Latency 측정
- Error rate 체크
- Data Drift 감지
```

#### 5. 자동화 (CI/CD)
```
- 자동 학습
- 자동 테스트
- 자동 배포
- GitHub Actions, Jenkins
```

#### 6. 협업 및 버전 관리
```
- Git (코드)
- DVC (데이터)
- MLflow (실험)
```

#### 7. 보안 및 규정 준수
```
- 접근 제어
- 암호화
- 권한 관리
```

---

## Day 7~8이 MLOps 어디에 해당하냐면

```
Day 7
├── train.py         → Training 단계
├── pickle           → Model Artifact 관리
└── BentoML          → Serving 단계

Day 8
├── FastAPI          → API 서빙
└── Docker           → Deployment 단계 ← 오늘!

앞으로
├── CI/CD            → 자동화
├── Monitoring       → 성능 추적
├── Kubernetes       → 확장 가능한 배포
└── MLflow           → 실험 관리
```

---

## 핵심 3가지

```
1. ML System     = 모델을 사용하는 시스템
2. ML Lifecycle  = 모델 전체 과정 (순환 구조)
3. MLOps         = Lifecycle 자동화 + 운영
```

**관계:**
```
ML Lifecycle (큰 그림)
    ↓ 포함
ML System (일부 구현)
    ↓ 운영/자동화
MLOps (전체 통합)
```

---

## 백엔드 개발자 관점 정리

```
웹 개발             MLOps
───────────────────────────────
코드 배포           모델 배포
Git                 Git + DVC + MLflow
CI/CD               CI/CD + 재학습 자동화
모니터링            모니터링 + Data Drift 감지
버전 관리           코드 + 데이터 + 모델 버전
```

---

## 다음 할 것

- Day 9: MLOps 도구 생태계 이해
- Day 13~: Kubernetes
- Day 20~: AWS ECS 배포
- Week 5: Airflow 데이터 파이프라인
- Week 6: MLflow 모델 관리