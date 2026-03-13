# Day 23 실습 노트

**날짜**: 2026.03.13
**목표**: Airflow로 MovieLens 모델 재학습 자동화 DAG 완성

---

## 실습: movie_retrain_dag.py

### DAG 구조

```
load_data → preprocess → train_model → evaluate_and_save
```

### 최종 코드 요약

```python
@dag(dag_id="movie_retrain", schedule_interval=timedelta(days=1), ...)
def movie_retrain_pipeline():

    @task
    def load_data():
        # ratings.csv 없으면 샘플 데이터 생성
        return df.to_dict(orient="records")  # XCom은 JSON만 가능 → dict 변환

    @task
    def preprocess(raw_data: list):
        df = pd.DataFrame(raw_data)
        df = df.dropna()
        df = df[df["rating"].between(0.5, 5.0)]
        df = df.drop_duplicates(subset=["userId", "movieId"])
        return df.to_dict(orient="records")

    @task
    def train_model(clean_data: list):
        reader = Reader(rating_scale=(0.5, 5.0))
        dataset = Dataset.load_from_df(df[["userId", "movieId", "rating"]], reader)
        trainset, testset = train_test_split(dataset, test_size=0.2)
        model = SVD(n_factors=50, n_epochs=20)
        model.fit(trainset)
        rmse = accuracy.rmse(model.test(testset))
        return {"model": pickle.dumps(model).hex(), "rmse": rmse}  # bytes→hex

    @task
    def evaluate_and_save(train_result: dict):
        # best_rmse.txt와 비교 후 더 좋으면 저장
        if new_rmse < best_rmse:
            # best_model.pkl, best_rmse.txt 갱신
            return {"saved": True, "rmse": new_rmse}

    # DAG 실행 순서 정의
    raw = load_data()
    cleaned = preprocess(raw)
    result = train_model(cleaned)
    evaluate_and_save(result)
```

### 실행 결과

```
XCom - evaluate_and_save:
{'saved': True, 'rmse': 0.9560210840621078}
```

---

## 🔥 트러블슈팅

| 에러                                                | 원인                              | 해결                                              |
| --------------------------------------------------- | --------------------------------- | ------------------------------------------------- |
| `ModuleNotFoundError: No module named 'surprise'`   | Dockerfile에 scikit-surprise 없음 | `RUN pip install scikit-surprise` 추가            |
| `gcc not found` (surprise 빌드 에러)                | C 확장 빌드 도구 없음             | `RUN apt-get install -y gcc python3-dev` 추가     |
| `KeyError: 'user_id'`                               | 컬럼명 오타                       | `user_id` → `userId`, `movie_id` → `movieId` 수정 |
| `TypeError: 'NoneType' object is not subscriptable` | `train_model`에서 return 누락     | `return {"model": ..., "rmse": ...}` 추가         |

---

## 핵심 개념 정리

### XCom - Task 간 데이터 전달

```python
# return하면 자동으로 XCom에 저장
@task
def load_data():
    return df.to_dict()  # ← 이게 XCom에 저장됨

# 다음 task에서 파라미터로 받으면 자동으로 XCom에서 꺼내옴
@task
def preprocess(raw_data: list):  # ← 자동으로 XCom에서 가져옴
    ...
```

- XCom은 **JSON만 저장 가능** → DataFrame은 `.to_dict()`로 변환 필수
- NestJS로 치면 **req.body** - 다음 미들웨어로 데이터 전달하는 것과 동일

### pickle bytes → hex string 이유

```python
# pickle.dumps()는 bytes 반환
model_bytes = pickle.dumps(model)  # b'\x80\x05...'

# XCom은 JSON 직렬화 → bytes 저장 불가
# hex string으로 변환해서 저장
return {"model": model_bytes.hex()}  # '800495...'

# 꺼낼 때 역변환
model = pickle.loads(bytes.fromhex(train_result["model"]))
```

### float("inf") 패턴

```python
if os.path.exists(rmse_path):
    best_rmse = float(f.read())
else:
    best_rmse = float("inf")  # 첫 실행 → 무조건 저장되게
```

- NestJS로 치면 `const best = existingRecord ?? Infinity`

### Dockerfile - C 빌드 도구 필요한 패키지

```dockerfile
USER root
RUN apt-get update && apt-get install -y gcc python3-dev  # C 확장 빌드용

USER airflow
RUN pip install scikit-surprise  # surprise는 C 확장 포함
```

- `scikit-learn`은 바로 pip install 가능
- `scikit-surprise`는 C 코드 컴파일 필요 → gcc 먼저 설치

---

## ✅ 오늘 완성한 것

- [x] `movie_retrain_dag.py` - 전체 파이프라인 성공
- [x] XCom으로 Task 간 데이터 전달 확인
- [x] RMSE 0.956, saved: True 확인

## 📝 회고

- **배운 것**: XCom JSON 제약, pickle→hex 변환 패턴, surprise vs sklearn 차이
- **막혔던 부분**: return 누락으로 NoneType 에러, 컬럼명 오타(user_id vs userId)
- **내일 연결**: Drift 감지 DAG - RMSE가 임계값 초과하면 Slack 알림

## Git 커밋

```bash
git add .
git commit -m "Day 24: Airflow 모델 재학습 DAG 완성 (RMSE 0.956)"
git push
```
