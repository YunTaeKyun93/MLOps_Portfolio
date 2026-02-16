# Day 7 - CF 실습 노트

> 실습 완료 기준으로 작성

---

## 실습 환경

- OS: Windows
- Python 버전: 3.x (.venv 가상환경)
- 데이터: MovieLens 1M (ratings.dat 로컬 다운로드)

---

## 실습 흐름

### 1단계 - train_easy.py (탐색/이해용)

처음부터 함수형으로 짜지 않고, **절차형으로 먼저 눈으로 확인**하는 방식으로 시작.

```
데이터 로딩 → shape 확인
→ pivot_table로 Matrix 생성 → NaN 비율 확인
→ csr_matrix + cosine_similarity → 유사도 행렬 확인
→ 단일 유저 기준 안 본 영화 예측
→ predictions dict로 top10 추출
```

각 단계마다 print()로 데이터가 어떻게 변하는지 눈으로 확인하면서 진행.
이해가 된 다음 함수형으로 리팩토링.

### 2단계 - train.py (함수형 리팩토링)

train_easy.py에서 이해한 로직을 함수로 묶음:

```python
load_data()           # 데이터 로딩
build_matrix()        # User-Item Matrix 생성
compute_similarity()  # 코사인 유사도 계산
predict_rating()      # 평점 예측
evaluate()            # 정확도 측정
save_model()          # pickle 저장
```

### 3단계 - service.py (BentoML API 서빙)

pickle 로드 → predict_rating() 재사용 → BentoML 2.0으로 API 서빙

---

## 실습 결과

### 최종 Accuracy
```
38.2%

랜덤 예측      → 20%
전체 평균 예측 → 28%
CF (우리 방법) → 38.2%  ← 랜덤 대비 약 2배
```

### 단계별 소요 시간

| 단계 | 소요 시간 |
|------|---------|
| 데이터 로딩 | 수 초 |
| User-Item Matrix 생성 | 수 초 |
| 유사도 계산 (csr_matrix) | 약 5초 (3,648만 쌍 계산) |
| evaluate() 2만 건 예측 | 수 분 (tqdm으로 진행률 확인) |

---

## 막혔던 부분 & 해결 방법

### 1. timestamp 컬럼 누락
```python
# 문제
names=["user_id", "movie_id", "user_rating"]

# 해결 - ratings.dat는 컬럼이 4개
names=["user_id", "movie_id", "user_rating", "timestamp"]
```
컬럼명이 밀려서 사용자 수/영화 수가 뒤집혀 출력됨

### 2. train/test split 전에 matrix 생성 (데이터 누수)
```python
# 문제 - df 전체로 matrix 생성하면 test 데이터가 포함됨
matrix = build_matrix(df)

# 해결 - train_df로만 생성
train_df, test_df = train_test_split(df, test_size=0.02, random_state=42)
matrix = build_matrix(train_df)
```
train으로만 만들면 영화가 3706 → 3705개로 줄어듦
test에만 있는 영화 1개 = Cold Start 문제의 축소판

### 3. BentoML 2.0 문법 변화
```python
# 1.x 방식
svc = bentoml.Service("cf_recommender")

@svc.api(input=JSON(), output=JSON())
def predict(request: dict) -> dict:
    ...

# 2.0 방식
@bentoml.service
class CFRecommender:

    @bentoml.api
    def predict(self, request: dict) -> dict:
        ...
```
from bentoml.io import JSON import도 필요 없어짐

### 4. Windows curl JSON 따옴표 문제
```bash
# 문제 - Windows에서 작은따옴표 인식 안 됨
-d '{"user_id": 1, "movie_id": 1193}'

# 해결 1 - 큰따옴표 이스케이프
-d "{\"user_id\": 1, \"movie_id\": 1193}"

# 해결 2 - BentoML 2.0은 request 키로 감싸야 함
-d "{\"request\": {\"user_id\": 1, \"movie_id\": 1193}}"
```

---

## API 테스트 결과

```bash
curl -X POST http://localhost:3000/predict \
     -H "Content-Type: application/json" \
     -d "{\"request\": {\"user_id\": 1, \"movie_id\": 1193}}"
```

```json
{
    "user_id": 1,
    "movie_id": 1193,
    "predicted_rating": 4.41,
    "rounded_rating": 4
}
```

---

## 오늘 새로 알게 된 것

- csr_matrix: 95% NaN인 희소 행렬을 0 아닌 값만 저장해서 메모리 절약 + 속도 향상
- 데이터 누수(Data Leakage): test 데이터가 학습에 포함되면 정확도가 뻥튀기됨
- pickle vs joblib: DataFrame은 pickle, sklearn 모델/numpy 대용량 배열은 joblib
- BentoML Runner 불필요한 경우: BentoML Model Store에 등록 안 한 pickle은 그냥 직접 로드해서 사용
- 절차형 → 함수형 리팩토링: 먼저 눈으로 확인하고 이해한 다음 함수로 묶는 순서가 효과적

---
