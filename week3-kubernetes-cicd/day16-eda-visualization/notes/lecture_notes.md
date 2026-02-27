# Day 16 강의 노트 - Pandas 심화 + Matplotlib 시각화

**강의**: [B] Part1 Ch5-01~04
**날짜**: 2026.02.27

---

## 오늘 들은 강의

✅ 01. Pandas 기초 (25:18)
✅ 02. 데이터 변환 및 집계 (26:14)
✅ 03. Dask, 대용량 데이터 처리 (26:34)
✅ 04. Matplotlib을 통한 데이터 시각화 (18:28)

---

## 01. Pandas 기초

### NumPy vs Pandas

```python
# NumPy - 수치 계산, 모델 입력
array([[25, 70000],
       [30, 80000]])

# Pandas - 데이터 조작, 전처리
   Age  Salary
0   25  70000
1   30  80000
```

**흐름:**

```
CSV → Pandas (전처리) → .to_numpy() → 모델 입력
```

### fit vs transform 핵심

```python
# 학습 때만 fit
scaler.fit(X_train)      # 평균/표준편차 기억
scaler.transform(X_train)

# 추론 때는 transform만
scaler.transform(X_test)  # 학습 기준으로 변환
# scaler.fit(X_test) ← 절대 금지! 기준이 달라짐
```

### 백엔드 연결

```
fit      = API 검증 기준 정하기 (한 번만)
transform = 그 기준으로 요청 검증 (매번)
```

pipeline = Pipeline([
("scaler", StandardScaler()),
("model", LogisticRegression())
])

# 학습

pipeline.fit(X_train, y_train)

# 추론

pipeline.predict(X_test)

```

Pipeline으로 묶으면:
```

fit(X_train) 호출 시
→ scaler.fit(X_train) 자동
→ model.fit(scaler.transform(X_train)) 자동

predict(X_test) 호출 시
→ scaler.transform(X_test) 자동 (fit 안 함!)
→ model.predict(...) 자동

```

즉 "scaler가 학습 기준으로만 transform 해야 한다"는 걸 Pipeline이 자동으로 보장해줌~~~

백엔드 비유:
```

미들웨어 체인이랑 같아
Request → 인증 미들웨어 → 검증 미들웨어 → 컨트롤러
순서대로 자동 실행되는 것처럼

---

## 02. 데이터 변환 및 집계

### 자주 쓰는 것만 정리

```python
# 데이터 로딩
df = pd.read_csv("data.csv", dtype={"id": str})

# 필터링
df[df["rating"] >= 4]
df[(df["rating"] >= 4) & (df["user_id"] == 1)]  # and 아니고 &

# groupby + agg (SQL GROUP BY와 동일)
df.groupby("user_id")["rating"].mean()
df.groupby("movie_id")["rating"].count()

# 정렬
df.sort_values("rating", ascending=False)

# 상위 N개
df.head(10)
```

### 백엔드 연결

```python
# Pandas groupby
df.groupby('user_id')['rating'].mean()

# SQL
SELECT user_id, AVG(rating) FROM ratings GROUP BY user_id
```

완전히 같은 개념.

---

## 03. Dask (개념만)

Pandas는 메모리 기반 → 대용량 데이터 한계

Dask = Pandas 문법 유지 + 병렬 처리 + 지연 실행

```python
ddf = dd.from_pandas(df, npartitions=5)
result = ddf.mean().compute()  # compute() 호출해야 실행
```

**지금 당장 필요 없음.** Airflow, Feature Store 할 때 다시 보기.

---

## 04. Matplotlib 시각화

### 상황별 그래프 선택 (이것만 외우기)

```
분포 보기    → histogram, bar
관계 보기    → scatter
시간 흐름    → line
비율 보기    → pie, bar
```

### 기본 구조

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(x, y)           # or bar, hist, scatter
plt.title('제목')
plt.xlabel('X축')
plt.ylabel('Y축')
plt.tight_layout()
plt.savefig('output.png')  # 파일 저장
plt.show()
```

### MLOps에서 쓰이는 곳

```
EDA → 데이터 분포 확인
모델 평가 → Loss curve, ROC curve, Confusion matrix
모니터링 → Drift 감지 시각화
```

---

## ✏️ 핵심 질문 5개

### Q1. groupby를 백엔드 관점으로 설명하면?

**A**: SQL의 GROUP BY와 동일. 특정 키를 기준으로 데이터를 묶어서 집계하는 작업.

### Q2. fit은 언제만 써야 하나?

**A**: 학습 데이터(X_train)에만. 테스트 데이터에 fit하면 기준이 달라져서 모델이 엉뚱한 값을 받음. transform만 사용.

### Q3. apply() 대신 뭘 써야 하나?

**A**: 벡터 연산. `np.where()` 등. apply()는 편하지만 느리고, 벡터 연산이 훨씬 빠름.

### Q4. Dask가 필요한 상황은?

**A**: 데이터가 메모리에 안 들어갈 때. 일반 전처리는 Pandas로 충분.

### Q5. 시각화에서 그래프 선택 기준은?

**A**: 분포→histogram/bar, 관계→scatter, 시간흐름→line, 비율→pie/bar.

---

## 💬 오늘 강의 한 줄 요약

> Pandas는 문법보다 "언제 어떻게 쓰는지"가 중요하고, 코드는 찾아가며 써도 된다. 중요한 건 상황 판단력.
