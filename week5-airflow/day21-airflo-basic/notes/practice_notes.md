# Day 21 실습 노트

**날짜**: 2026.03.09
**목표**: Docker Compose로 Airflow 환경 구축 + ML 학습 파이프라인 DAG 작성 + XCom 실습

---

## 실습 1: Dockerfile 작성

### 목표

- [x] Airflow + ML 라이브러리 환경 구축

### 핵심 코드

```dockerfile
FROM apache/airflow:2.7.3
USER airflow
RUN pip install --no-cache-dir pandas scikit-learn
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
```

### 백엔드 연결

```
FROM apache/airflow  = node:18 베이스 이미지
pip install          = npm install
LOAD_EXAMPLES=False  = 불필요한 예제 DAG 비활성화
```

---

## 실습 2: Docker Compose 구성 (트러블슈팅 포함)

### 0단계: docker run으로 먼저 성공 → 리팩토링 결정

처음에는 docker-compose 없이 docker run으로 실행했고 정상 동작했다.

```bash
docker build -t airflow_practice .
docker run -p 8080:8080 \
  -v ./dags:/opt/airflow/dags \
  -v ./logs:/opt/airflow/logs \
  -v ./plugins:/opt/airflow/plugins \
  airflow_practice webserver
```

그런데 매번 실행할 때마다:

```
1. DB 초기화 명령 직접 입력
   docker exec -it airflow_practice airflow db init

2. 유저 생성 명령 직접 입력
   docker exec -it airflow_practice airflow users create \
     --username admin --password admin ...

3. 볼륨 옵션 매번 -v 플래그로 작성
4. scheduler는 별도 터미널에서 또 docker run
```

**리팩토링 이유**:

```
매번 유저 정보 입력 귀찮음
볼륨도 docker run CLI로 매번 치기 귀찮음
→ docker-compose.yml 한 파일로 관리하면 docker compose up 한 번으로 끝
```

NestJS로 비유하면:

```
docker run 방식  = 터미널에서 node dist/main.js 직접 실행
docker compose  = package.json scripts에 "start" 명령 등록해두는 것
```

---

### 1단계: 단순 실행 시도 (실패)

처음 작성한 docker-compose.yml:

```yaml
version: "3"
services:
  airflow:
    build: .
    container_name: airflow_practice
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    command: webserver
```

**문제**: webserver만 뜨고 scheduler 없음 + DB 초기화 없음.

---

### 2단계: command에 초기화 로직 추가 시도 (실패)

```yaml
command: >
  bash -c "
  airflow db init &&
  airflow users create ... &&
  airflow webserver -p 8080 &
  airflow scheduler
  "
```

**에러**:

```
ERROR: You need to initialize the database
컨테이너 상태: Exited (1)
```

**근본 원인**:
`apache/airflow` 이미지의 ENTRYPOINT가 고정되어 있음:

```
ENTRYPOINT ["airflow"]
```

그래서 `command: bash -c "..."` 를 쓰면 실제로는:

```
airflow bash -c "airflow db init ..."
```

이렇게 실행됨. `bash`를 airflow 서브커맨드로 인식해버려서 에러 발생.

**백엔드 연결**:

```
NestJS Dockerfile에서 ENTRYPOINT ["node"] 설정 후
command: "dist/main.js" 쓰면
→ node dist/main.js 로 실행됨 (정상)

command: "bash -c 'node dist/main.js'"
→ node bash -c '...' 로 실행됨 (에러!)
```

---

### 3단계: 3개 서비스로 분리 (성공)

**핵심 해결책**: `entrypoint: /bin/bash` 로 ENTRYPOINT 덮어씌우기

```yaml
version: "3"
services:
  airflow-init:
    build: .
    container_name: airflow_init
    environment:
      - AIRFLOW__CORE__EXECUTOR=SequentialExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/airflow.db
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - airflow-db:/opt/airflow
    entrypoint: /bin/bash # ← ENTRYPOINT 덮어씌우기 (핵심!)
    command: -c "airflow db init && airflow users create --username admin --password admin --firstname admin --lastname admin --role Admin --email admin@example.com"

  airflow-webserver:
    build: .
    container_name: airflow_webserver
    depends_on:
      - airflow-init # ← init 완료 후 실행
    ports:
      - "8080:8080"
    environment:
      - AIRFLOW__CORE__EXECUTOR=SequentialExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/airflow.db
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - airflow-db:/opt/airflow # ← init에서 만든 DB 공유
    command: webserver

  airflow-scheduler:
    build: .
    container_name: airflow_scheduler
    depends_on:
      - airflow-init # ← init 완료 후 실행
    environment:
      - AIRFLOW__CORE__EXECUTOR=SequentialExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/airflow.db
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - airflow-db:/opt/airflow # ← init에서 만든 DB 공유
    command: scheduler

volumes:
  airflow-db: # ← 3개 컨테이너 공유 볼륨
```

**3개 서비스 역할**:

```
airflow-init      = DB 마이그레이션 (typeorm migration:run)
airflow-webserver = API 서버 (nest start)
airflow-scheduler = 백그라운드 워커 (bull queue worker)
```

**depends_on 역할**:

```
DB 초기화 전에 webserver/scheduler가 뜨면 에러
→ depends_on으로 init 완료 보장
= NestJS에서 DB 연결 전에 서버 시작하면 안 되는 것과 동일
```

**airflow-db volume 역할**:

```
init에서 만든 sqlite DB를
webserver, scheduler가 같이 읽어야 함
→ 같은 volume 마운트해서 공유
```

### 실행 순서

```bash
# 기존 컨테이너/볼륨 완전 초기화
docker compose down -v

# 1단계: DB 초기화 + admin 계정 생성
docker compose up airflow-init
# 로그에 "Admin user admin created" 뜨면 완료

# 2단계: webserver + scheduler 실행
docker compose up airflow-webserver airflow-scheduler
```

### 접속 확인

```
http://localhost:8080
admin / admin 로그인 ✅
```

---

## 실습 3: ML 파이프라인 DAG 작성

### 목표

- [x] feature_engineering → train_rf/gb (병렬) → select_best_model DAG 작성
- [x] XCom으로 Task 간 데이터 전달
- [x] 전체 파이프라인 실행 성공

### DAG 구조

```
feature_engineering
        |
   /         \
train_rf   train_gb  (병렬 실행)
        |
select_best_model
```

코드:

```python
t1 >> [t2, t3] >> t4
```

### 핵심 코드

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

dag = DAG(
    dag_id="model_training_selection",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
)

def feature_engineering(ti):
    from sklearn.datasets import load_iris
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    # XCom push - Task 간 데이터 전달
    ti.xcom_push(key="X_train", value=X_train.to_json())
    ti.xcom_push(key="X_test", value=X_test.to_json())
    ti.xcom_push(key="y_train", value=y_train.to_json())
    ti.xcom_push(key="y_test", value=y_test.to_json())

def train_model(model_name, ti):
    # XCom pull - feature_engineering에서 push한 데이터 가져오기
    X_train = pd.read_json(ti.xcom_pull(key="X_train", task_ids="feature_engineering"))
    X_test = pd.read_json(ti.xcom_pull(key="X_test", task_ids="feature_engineering"))
    y_train = pd.read_json(ti.xcom_pull(key="y_train", task_ids="feature_engineering"), typ="series")
    y_test = pd.read_json(ti.xcom_pull(key="y_test", task_ids="feature_engineering"), typ="series")

    model = RandomForestClassifier() if model_name == "RandomForest" else GradientBoostingClassifier()
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    ti.xcom_push(key=f"performance_{model_name}", value=acc)

def select_best_model(ti):
    rf = ti.xcom_pull(key="performance_RandomForest", task_ids="train_rf")
    gb = ti.xcom_pull(key="performance_GradientBoosting", task_ids="train_gb")
    best = "RandomForest" if rf > gb else "GradientBoosting"
    Variable.set("best_model", best)
    print("Best model:", best)
    return best

with dag:
    t1 = PythonOperator(task_id="feature_engineering", python_callable=feature_engineering)
    t2 = PythonOperator(task_id="train_rf", python_callable=train_model, op_kwargs={"model_name": "RandomForest"})
    t3 = PythonOperator(task_id="train_gb", python_callable=train_model, op_kwargs={"model_name": "GradientBoosting"})
    t4 = PythonOperator(task_id="select_best_model", python_callable=select_best_model)
    t1 >> [t2, t3] >> t4
```

### 실행 결과

```
feature_engineering  → success ✅
train_rf             → success ✅  (accuracy: 0.9555)
train_gb             → success ✅  (accuracy: 0.9555)
select_best_model    → success ✅  (best: GradientBoosting)
```

XCom 저장 확인 (Admin → XComs):

```
X_train, X_test, y_train, y_test    ← feature_engineering
performance_RandomForest: 0.9555    ← train_rf
performance_GradientBoosting: 0.9555← train_gb
return_value: GradientBoosting      ← select_best_model
```

### 백엔드 연결

```
XCom push/pull  = Redis SET/GET (Task 간 캐시 공유)
Variable.set    = 전역 설정값 저장 (like process.env 동적 업데이트)
op_kwargs       = PythonOperator에 파라미터 전달 (like 함수 인자)
task_ids        = 어느 Task의 값인지 지정 (like Redis key prefix)
```

---

## 🔥 트러블슈팅

| 에러                                  | 원인                                 | 해결                                  |
| ------------------------------------- | ------------------------------------ | ------------------------------------- |
| `You need to initialize the database` | DB 초기화 전에 webserver 실행 시도   | airflow-init 서비스 분리 + depends_on |
| `Exited (1)` 컨테이너 즉시 종료       | ENTRYPOINT 충돌로 프로세스 시작 실패 | `entrypoint: /bin/bash` 로 덮어쓰기   |
| `container is not running`            | 컨테이너가 바로 종료돼서 exec 불가   | 위와 동일                             |
| volume 경로 오류 `/usr/local/airflow` | Airflow 공식 경로는 `/opt/airflow`   | volume 경로 `/opt/airflow`로 수정     |
| XCom UI 탭 안 보임                    | Airflow 2.7.x에서 UI 변경됨          | Admin → XComs 메뉴에서 확인           |

---

## 프로젝트 구조

```
airflow_practice/
├── Dockerfile
├── docker-compose.yml
├── dags/
│   └── model_training_dag.py
├── logs/
└── plugins/
```

---

## ✅ 오늘 완성한 것

- [x] Dockerfile (Airflow + ML 라이브러리)
- [x] docker-compose.yml (3 서비스: init/webserver/scheduler)
- [x] dags/model_training_dag.py (ML 학습 파이프라인)
- [x] XCom 데이터 전달 확인

---

## 📝 회고

- **배운 것**: Airflow ENTRYPOINT 구조, XCom으로 Task 간 데이터 전달, 3개 서비스로 분리하는 패턴
- **막혔던 부분**: docker-compose command + Airflow ENTRYPOINT 충돌 → entrypoint 덮어쓰기로 해결
- **핵심 인사이트**: XCom은 소량 데이터 전달용. 실무에서는 S3 경로만 XCom으로 전달
- **내일 연결**: ETL 파이프라인 DAG 작성 (CSV → 전처리 → DB 저장)

---

## Git 커밋

```bash
git checkout -b feat/day22-airflow-dag
git add .
git commit -m "feat: Airflow Docker 환경 구축 + ML 학습 파이프라인 DAG 작성"
git push origin feat/day22-airflow-dag
```
