# Day 21 강의 노트

**강의**: [P] Part2 Ch3-09~10 + [B] Part3 Ch2-06 - Workflow Management + Airflow
**날짜**: 2026.03.09

---

## 오늘 들은 강의

✅ [P] Part2 Ch3-09 - Workflow Management 이론 (17:11)
✅ [P] Part2 Ch3-10 - Airflow Workflow Management 실습 (1:00:03)
✅ [B] Part3 Ch2-06 - Airflow 시작하기 (26:14)

---

## 1. Workflow Management란

### 핵심 개념

일반 cron job vs Airflow:

```
cron:    "매일 9시에 스크립트 실행"
Airflow: "매일 9시에 A 실행
          → A 성공하면 B, C 병렬 실행
          → B, C 끝나면 D 실행
          → 실패 시 Slack 알림
          → 전체 히스토리 UI로 확인"
```

즉 Airflow = **cron job의 고급 버전**

### 백엔드 연결

```
Airflow DAG       = GitHub Actions workflow.yml
Task              = workflow의 각 step
Operator          = step에서 uses/run 지정하는 것
Scheduler         = GitHub Actions runner
schedule_interval = on: schedule (cron 표현식)
```

---

## 2. Airflow 구성요소

### DAG (Directed Acyclic Graph)

- Workflow 전체 흐름 정의
- 방향이 있고 (Directed) 순환이 없음 (Acyclic)
- 예시:

```
feature_engineering
        ↓
   train_rf  train_gb  (병렬)
        ↓
select_best_model
```

코드로:

```python
t1 >> [t2, t3] >> t4
```

### Task

- DAG 내부의 실행 단위
- 각 Task는 독립적으로 실행됨
- 성공/실패 상태 개별 관리

### Operator

Task 실행 방식 정의:

```
PythonOperator  = Python 함수 실행
BashOperator    = Bash 명령 실행
DockerOperator  = Docker 컨테이너 실행
```

### Scheduler

- DAG 파일 감시
- Task 실행 순서/시간 관리
- Task 실행 트리거

### Webserver

- Airflow UI 제공 (localhost:8080)
- DAG 상태 확인
- Task 로그 확인
- 수동 실행 (▶️ 버튼)

### Metadata Database

Airflow 내부 상태 저장소:

```
DAG 실행 상태
Task 상태
XCom 데이터
로그
Variables
Connections
```

---

## 3. XCom (Cross Communication)

Task 간 데이터 전달 방식.

### push

```python
ti.xcom_push(key='X_train', value=X_train.to_json())
```

### pull

```python
X_train = pd.read_json(
    ti.xcom_pull(key='X_train', task_ids='feature_engineering')
)
```

### 백엔드 연결

```
XCom   = Task 간 공유 메모리 (like Redis cache)
key    = cache key
push   = Redis SET
pull   = Redis GET
task_ids = 어느 Task가 저장한 값인지 지정
```

주의: XCom은 소량 데이터용. 대용량 데이터는 S3/DB에 저장하고 경로만 XCom으로 전달하는 게 실무 패턴.

---

## 4. DAG 작성 패턴

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

dag = DAG(
    dag_id="my_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False           # 과거 날짜 소급 실행 방지
)

def my_task(ti):
    # 작업 내용
    pass

with dag:
    t1 = PythonOperator(
        task_id="my_task",
        python_callable=my_task
    )
```

### schedule_interval 주요 옵션

```
"@daily"   = 매일 자정
"@hourly"  = 매시간
"@weekly"  = 매주
"0 9 * * *" = 매일 오전 9시 (cron 표현식)
None       = 수동 실행만
```

---

## 5. MLOps에서 Airflow의 역할

```
Data Ingestion      ← Task 1
     ↓
Feature Engineering ← Task 2
     ↓
Model Training      ← Task 3 (병렬 가능)
     ↓
Model Evaluation    ← Task 4
     ↓
Model Selection     ← Task 5
     ↓
Model Deployment    ← Task 6
```

이 전체 파이프라인을 **스케줄 기반으로 자동 실행**하는 게 Airflow의 역할.

---

## ✏️ 핵심 질문 5개

### Q1. DAG에서 Acyclic(비순환)이 왜 중요한가?

**A**: 순환이 있으면 Task가 무한 루프에 빠질 수 있음. A→B→A 이면 끝나지 않음. Airflow는 이를 방지하기 위해 DAG 등록 시 순환 여부를 검증함.

### Q2. catchup=False를 왜 쓰는가?

**A**: start_date가 과거이면 그 사이 기간을 모두 소급 실행함. 예를 들어 start_date가 1년 전이면 365번 실행됨. catchup=False로 방지.

### Q3. XCom의 한계는?

**A**: 기본적으로 DB에 저장되므로 대용량 데이터 전달에 부적합. 실무에서는 S3 경로나 DB ID만 XCom으로 전달하고 실제 데이터는 외부 저장소 사용.

### Q4. Scheduler와 Webserver를 분리하는 이유는?

**A**: 역할이 다름. Scheduler는 Task 실행 관리, Webserver는 UI 제공. 분리하면 독립적으로 스케일링/재시작 가능.

### Q5. PythonOperator vs BashOperator 언제 쓰는가?

**A**: Python 코드 실행은 PythonOperator, 쉘 명령/스크립트 실행은 BashOperator. ML 파이프라인은 대부분 PythonOperator 사용.

---

## 💬 오늘 강의 한 줄 요약

> Airflow는 ML 파이프라인의 각 단계를 순서/의존성/스케줄 기반으로 자동 실행해주는 orchestrator이며, XCom으로 Task 간 데이터를 전달한다.
