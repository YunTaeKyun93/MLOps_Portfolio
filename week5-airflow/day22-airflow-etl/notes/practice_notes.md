# Day 22 실습 노트

**날짜**: 2026.03.12
**목표**: Airflow ETL DAG 작성 (MovieLens CSV → 전처리 → SQLite 저장)

---

## 실습: MovieLens ETL 파이프라인 DAG

### 목표

- [x] TaskFlow API(@task) 방식으로 ETL DAG 작성
- [x] Extract: 샘플 데이터 생성 (ratings.csv 없을 때)
- [x] Transform: 결측치 제거 + 타입 변환 + 중복 제거
- [x] Load: SQLite DB 저장
- [x] XCom으로 Task 간 데이터 전달 확인

---

## DAG 구조

```
extract → transform → load
  ↓           ↓          ↓
8행 추출   6행 정제   DB 저장
(nan 포함) (nan 제거)  (6행)
```

---

## 핵심 코드

### DAG 선언

```python
@dag(
    dag_id="movielens_etl",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "movielens"],
)
def movielens_etl_pipeline():
```

### TaskFlow API 의존성 연결

```python
raw = extract()          # Task1 실행 + return값
cleaned = transform(raw) # Task2 실행 (raw 자동 전달)
load(cleaned)            # Task3 실행 (cleaned 자동 전달)
```

### Transform 핵심

```python
df = df.dropna()                              # 결측치 제거
df["userId"] = df["userId"].astype(int)       # float → int
df = df[df["rating"].between(0.5, 5.0)]       # 범위 필터
df = df.drop_duplicates(subset=["userId", "movieId"])  # 중복 제거
```

### Load (SQLite 저장)

```python
conn = sqlite3.connect(db_path)
df.to_sql("ratings", conn, if_exists="replace", index=False)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM ratings")
count = cursor.fetchone()[0]  # (6,) → 6
conn.close()
```

---

## XCom 실행 결과

| Task      | 데이터                              | 행수 |
| --------- | ----------------------------------- | ---- |
| extract   | userId: 1.0 (float, nan 포함)       | 8행  |
| transform | userId: 1 (int, nan 제거)           | 6행  |
| load      | {'saved_rows': 6, 'db_path': '...'} | -    |

---

## 백엔드 연결

| ETL 코드            | NestJS 개념               |
| ------------------- | ------------------------- |
| `sqlite3.connect()` | `DataSource.initialize()` |
| `cursor.execute()`  | `em.query()`              |
| `df.to_sql()`       | `repository.save()`       |
| `conn.close()`      | `dataSource.destroy()`    |
| `fetchone()[0]`     | `result[0].count`         |

---

## 🔥 트러블슈팅

| 상황                              | 원인                                | 해결                          |
| --------------------------------- | ----------------------------------- | ----------------------------- |
| Pylance `airflow.decorators` 경고 | 로컬에 Airflow 미설치               | Docker 안에서 실행되므로 무시 |
| userId가 float으로 읽힘           | None 섞이면 pandas가 float으로 처리 | dropna() 후 astype(int)       |

---

## ✅ 오늘 완성한 것

- [x] `movielens_etl_dag.py`: ETL 파이프라인 DAG
- [x] Airflow UI에서 전체 Task success 확인
- [x] XCom 데이터 흐름 확인

---

## 📝 회고

- **배운 것**: TaskFlow API(@task)로 선언적 파이프라인 작성, ETL 개념 실습
- **어제와 차이**: PythonOperator → @task 데코레이터로 코드 간결해짐
- **내일 연결**: 모델 재학습 자동화 DAG (수집 → 전처리 → 학습 → 평가)

---

## Git 커밋

```bash
git add week5-airflow/
git commit -m "feat: Day22 MovieLens ETL DAG 작성 (Extract→Transform→Load)"
git push origin feat/day22-airflow-etl
```
