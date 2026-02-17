# Day 7 — Collaborative Filtering Recommender

MovieLens 1M 데이터로 **Collaborative Filtering 추천 시스템 구현 + BentoML API 서빙**

---

## 프로젝트 목표

ML 알고리즘 이해 → 함수형 리팩토링 → API 서빙 파이프라인 구축

---

## 학습 목표

- Collaborative Filtering 개념 이해
- User-Item Matrix 생성 및 코사인 유사도 계산
- train/test split + 정확도 평가
- pickle 기반 모델 저장
- BentoML 2.0 API 서빙
- Matrix Factorization 개념 이해

---

## 설계 의도

### 1. pickle을 사용한 이유

| 구분 | pickle | joblib |
|------|--------|--------|
| 주 용도 | 일반 Python 객체 | 대용량 Numpy / sklearn |
| 특징 | 범용적, 가벼움 | 메모리 매핑 최적화 |
| 결정 | Pandas DataFrame 저장 목적 | 불필요 |

현재 데이터는 DataFrame 기반이므로 pickle로 충분함.

---

### 2. BentoML Runner를 사용하지 않은 이유

```
Runner 필요   → BentoML Model Store 모델
Runner 불필요 → pickle / 사용자 정의 함수
```

Day 7 모델은 BentoML Model Store에 등록된 모델이 아니므로
직접 로드하는 구조를 사용함.

---

### 3. train_easy → train 순서

```
train_easy.py → 절차형
train.py      → 함수형
```

절차형으로 데이터 흐름을 먼저 이해하고  
이후 함수형으로 리팩토링.

---

### 4. csr_matrix 사용 이유

User-Item Matrix:

```
6040 × 3706 = 22,376,240 cells
95.5% sparse
```

csr_matrix 사용 이유:

- 메모리 절약
- 연산 속도 향상
- cosine_similarity와 호환

```
NaN → fillna(0)
→ csr_matrix 변환
```

---

### 5. Data Leakage 방지

matrix는 반드시 `train_df`로만 생성.

test 데이터가 포함되면:

```
"답지 보고 시험 보는 상황"
```

실제 결과:
```
3706 movies → 3705 movies
(test에만 존재하는 영화 1개)
```

---

## BentoML 1.x vs 2.0

### BentoML 1.x

```python
svc = bentoml.Service("cf_recommender")

@svc.api(input=JSON(), output=JSON())
def predict(request: dict) -> dict:
    ...
```

---

### BentoML 2.0

```python
@bentoml.service
class CFRecommender:
    def __init__(self):
        self.matrix = load_pickle(...)

    @bentoml.api
    def predict(self, user_id: int, movie_id: int) -> dict:
        return {"predicted_rating": score}
```

---

## 실행 방법

### 패키지 설치

```bash
pip install bentoml scikit-learn pandas numpy matplotlib tqdm
```

### 모델 학습

```bash
python src/train.py
```

### API 실행

```bash
bentoml serve src.service:CFRecommender --reload
```

---

## API 테스트

```bash
curl -X POST http://localhost:3000/predict \
     -H "Content-Type: application/json" \
     -d "{\"request\": {\"user_id\": 1, \"movie_id\": 1193}}"
```

응답 예시:

```json
{
  "user_id": 1,
  "movie_id": 1193,
  "predicted_rating": 4.41,
  "rounded_rating": 4
}
```

---

## 성능 벤치마크

| 방법 | Accuracy | 설명 |
|------|----------|------|
| Random | ~20% | baseline |
| Mean | ~28% | 전체 평균 |
| CF | 38.2% | 현재 구현 |
| MF / SVD | 55~65% | Next step |

---

## 프로젝트 구조

```
day7-cf-recommender/
├── notes/
│   ├── lecture_notes.md
│   ├── lecture_notes2.md
│   └── practice_notes.md
│
├── src/
│   ├── train_easy.py
│   ├── train.py
│   └── service.py
│
├── data/ml-1m/
│   └── ratings.dat
│
└── outputs/
    ├── user_item_matrix.pkl
    └── user_similarity.pkl
```

---

## 참고

Day 6 → BentoML 기본 서빙 (Titanic)  
Day 8 → Docker + Cloud Deployment  
Dataset → MovieLens 1M
