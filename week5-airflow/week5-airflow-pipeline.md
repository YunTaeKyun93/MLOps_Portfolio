# Week 5 - Airflow ML 파이프라인

Apache Airflow로 MovieLens 데이터 ETL, 모델 자동 재학습, Drift 감지 파이프라인 구현.

---

## 전체 구조

```
[Day 22] movielens_etl        CSV → 전처리 → SQLite 저장
              ↓
[Day 23] movie_retrain         매일 SVD 모델 재학습 → 성능 비교 후 저장
              ↓
[Day 24] drift_detection_dag   RMSE 모니터링 → Drift 감지 → 자동 재학습 트리거
```

---

## 환경

```yaml
# docker-compose.yml 기반
- Airflow 2.x (LocalExecutor)
- Python 3.11
- 포트: localhost:8080
- 데이터 볼륨: /opt/airflow/data/
```

---

## DAG 1. movielens_etl (Day 22)

### 개요

MovieLens ratings 데이터를 추출 → 전처리 → SQLite에 적재하는 ETL 파이프라인.

### 플로우

```
extract → transform → load
```

### 태스크 상세

**extract**

- `/opt/airflow/data/ratings.csv` 로드
- 파일 없을 시 샘플 데이터 자동 생성 (개발 환경 대응)
- 반환: `list[dict]` (XCom으로 다음 태스크에 전달)

**transform**

- 결측치 제거 (`dropna`)
- 타입 캐스팅 (`userId`, `movieId` → int, `rating` → float)
- 유효 평점 필터링 (`0.5 ~ 5.0`)
- 중복 제거 (`userId + movieId` 기준)

**load**

- SQLite(`movielens.db`) `ratings` 테이블에 저장
- `if_exists="replace"` → 매일 전체 갱신

### 스케줄

```python
schedule_interval=timedelta(days=1)
```

### 백엔드 관점

```
extract   = DB에서 raw 데이터 조회하는 Repository 계층
transform = request body 검증하는 Validation Pipe / 미들웨어
load      = 가공된 데이터를 DB에 upsert하는 Service 계층
XCom      = Task 간 데이터 전달 = NestJS req.body를 다음 미들웨어로 넘기는 것
```

---

## DAG 2. movie_retrain (Day 23)

### 개요

매일 SVD 모델을 재학습하고, 기존 모델보다 성능이 좋을 때만 저장하는 파이프라인.

### 플로우

```
load_data → preprocess → train_model → evaluate_and_save
```

### 태스크 상세

**load_data**

- `/opt/airflow/data/ratings.csv` 로드
- 없을 시 샘플 데이터 생성 (1,000건)

**preprocess**

- 결측치 제거, 타입 캐스팅, 유효 평점 필터링, 중복 제거

**train_model**

- scikit-surprise SVD (n_factors=50, n_epochs=20)
- train/test split 8:2
- RMSE 계산
- 모델을 `bytes → hex string`으로 직렬화 후 XCom 전달

> **왜 hex string?**  
> Airflow XCom은 JSON 직렬화 기반. bytes는 직접 전달 불가 → hex string 변환 후 전달.  
> NestJS에서 Buffer를 JSON으로 직렬화할 때 base64 쓰는 것과 동일한 이유.

**evaluate_and_save**

- `best_rmse.txt`에서 이전 RMSE 로드
- 새 RMSE < 이전 RMSE → `best_model.pkl` + `best_rmse.txt` 갱신
- 새 RMSE >= 이전 RMSE → 기존 모델 유지

### 성능

- **RMSE: 0.956** (평점 1~5 척도 기준, 오차 약 ±0.956점)

### 스케줄

```python
schedule_interval=timedelta(days=1)  # 매일 자동 재학습
```

### 백엔드 관점

```
DAG 전체          = 스케줄러가 매일 실행하는 배치 Job
evaluate_and_save = 배포 전 canary 테스트 통과 여부 확인과 동일한 개념
best_rmse.txt     = 현재 프로덕션 모델의 성능 기준선 (rollback 기준)
```

---

## DAG 3. drift_detection_dag (Day 24)

### 개요

모델 성능을 모니터링하다가 Drift 감지 시 자동으로 재학습을 트리거하는 파이프라인.

### 플로우

```
check_model_performance → detect_drift → retrain_model → notify
```

### 태스크 상세

**check_model_performance**

- 현재 서빙 중인 모델의 RMSE 측정
- baseline_rmse: `0.956` (Day 24에서 학습한 모델 기준)
- 현재 구현: `random.uniform(0.85, 1.2)` 시뮬레이션

**detect_drift**

- threshold = `baseline_rmse × 1.1` (10% 초과 시 Drift 판정)
- 0.956 × 1.1 = **1.052** 초과 시 `is_drift = True`

**retrain_model**

- `is_drift=True` → 재학습 실행
- `is_drift=False` → 스킵 (불필요한 재학습 방지)

**notify**

- Drift 여부 + 새 RMSE 알림 출력
- 실제 운영 시 Slack webhook 연동 가능

### Drift 감지 기준

```
is_drift = current_rmse > baseline_rmse * 1.1

예시:
- current_rmse = 0.98 → 0.98 < 1.052 → Drift 없음
- current_rmse = 1.10 → 1.10 > 1.052 → Drift 감지 → 재학습
```

### 스케줄

```python
schedule="@daily"
```

### 백엔드 관점

```
Drift 감지    = API 응답시간 p99 임계값 초과 시 알람 발생하는 것과 동일
threshold     = SLO(Service Level Objective) 기준선
재학습 트리거 = 알람 → 자동 스케일아웃 트리거와 같은 개념
notify        = PagerDuty / Slack 알림
```

---

## 핵심 개념 정리

### TaskFlow API (`@task` 데코레이터)

```python
# 기존 방식
def my_func():
    ...
t1 = PythonOperator(task_id="my_func", python_callable=my_func)

# TaskFlow API (Day 24~25에서 사용)
@task
def my_func():
    ...
```

- `@task` 데코레이터 = NestJS의 `@Get()`, `@Post()` 같은 AOP 방식
- 태스크 의존성을 `>>` 대신 함수 호출로 자연스럽게 표현

### XCom (Cross-Communication)

```python
# 자동으로 반환값이 XCom에 저장됨
@task
def extract():
    return data  # → XCom에 저장

@task
def transform(raw_data):  # → XCom에서 자동으로 꺼내옴
    ...
```

- TaskFlow API에서는 함수 반환값이 자동으로 XCom에 저장/로드
- NestJS의 `req` 객체를 미들웨어 체인에 넘기는 것과 동일

### my_dag.py vs TaskFlow API 차이

```python
# my_dag.py (전통적 방식) - XCom 수동 push/pull
ti.xcom_push(key="X_train", value=X_train.to_json())
X_train = pd.read_json(ti.xcom_pull(key="X_train", task_ids="feature_engineering"))

# TaskFlow API (현대적 방식) - 함수 반환값으로 자동 처리
@task
def feature_engineering():
    return {"X_train": ..., "X_test": ...}  # 자동 XCom 저장

@task
def train_model(data):  # 자동 XCom 로드
    X_train = data["X_train"]
```

---

## 트러블슈팅

| 문제                                | 원인                            | 해결                                                  |
| ----------------------------------- | ------------------------------- | ----------------------------------------------------- |
| XCom에 bytes 전달 불가              | Airflow XCom은 JSON 직렬화 기반 | `pickle.dumps(model).hex()` → hex string 변환 후 전달 |
| DAG가 Airflow UI에 안 보임          | `dag()` 함수 호출 누락          | 파일 하단에 `movie_retrain_pipeline()` 호출 추가      |
| Docker Compose 실행 시 DB 연결 오류 | Airflow 초기화 전 DAG 실행      | `airflow db init` 후 웹서버 실행 순서 확인            |

---

## 개선 예정

- [ ] Slack webhook 연동 (notify 태스크 실제 알림)
- [ ] `check_model_performance` 실제 모델 RMSE 측정으로 교체 (현재 시뮬레이션)
- [ ] MLflow 연동 (실험 추적 + 모델 레지스트리)
- [ ] S3에 모델 저장 (현재 로컬 파일 시스템)
