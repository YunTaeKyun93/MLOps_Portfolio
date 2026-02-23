# Day 7 - Ch1. Collaborative Filtering 강의노트

> Week 2 | MLOps 서빙/배포 파트  
> 강의: [B] Part2 Ch1 (1:02:26)

---

## Ch1-01. 추천 시스템 개요 및 소개 (22:32)

### 핵심 개념

**추천 시스템의 두 가지 방향:**

```
1. Content-based Filtering (콘텐츠 기반)
   → 아이템 자체의 특성으로 추천
   → 예: 액션 영화 봤으면 → 다른 액션 영화 추천

2. Collaborative Filtering (협업 필터링) ← 오늘 배울 것!
   → 사용자들의 행동 패턴으로 추천
   → 예: 나와 비슷한 사람들이 좋아한 것 추천
```

### CF의 핵심 아이디어

```
"나와 비슷한 취향의 사람들이 좋아한 것을 나도 좋아할 것이다"

User A: 영화1(5점), 영화2(4점), 영화3(?)
User B: 영화1(5점), 영화2(5점), 영화3(5점)
→ A와 B가 비슷하네?
→ A도 영화3을 좋아할 것 같다!
```

### CF의 두 가지 방식

```
1. User-based CF
   → 비슷한 사용자 찾기
   → "너랑 비슷한 사람들이 이거 좋아해"

2. Item-based CF
   → 비슷한 아이템 찾기
   → "이 영화 좋아하면 저 영화도 좋아할 거야"
```

### Rating Matrix 구조

```
User-Item Matrix = Sparse Matrix (희소 행렬)

       영화1  영화2  영화3  영화4
User1   5     4     ?     ?
User2   ?     5     3     ?
User3   4     ?     ?     5
User4   ?     ?     4     3

? = 아직 안 본 영화 (평점 없음)
→ 이 빈칸을 채우는 게 추천 시스템의 목표!
→ 95% 이상이 빈칸 = Sparse
```

### 실생활 서비스 예시

```
- Netflix (영화/드라마 추천)
- YouTube (영상 추천)
- Amazon (상품 추천)
- Spotify (음악 추천)
- 당근마켓 (중고거래 추천)
```

---

## Ch1-02. CF의 기본 원리 및 구성 요소 (18:53)

### 유사도 계산 방법

#### 1. Cosine Similarity (코사인 유사도) ← 제일 많이 씀!

```python
from sklearn.metrics.pairwise import cosine_similarity

# User A: [5, 4, ?, 3]
# User B: [4, 5, ?, 4]
# → 벡터 간 각도로 유사도 계산
# → 값의 크기보다 "방향"이 중요

cosine_similarity(user_a, user_b)
# 0 = 전혀 다름
# 1 = 완전 같음
```

#### 2. Pearson Correlation (피어슨 상관계수)

```
- 사용자별 평점 스케일 차이 보정
- User A가 후하게 주는 사람이면 자동 보정
- -1 ~ 1 사이 값
```

#### 3. Euclidean Distance (유클리드 거리)

```
- 실제 거리 계산
- 좌표 평면에서의 직선 거리
- 거리가 가까울수록 유사
```

### Explicit vs Implicit Feedback

```
Explicit (명시적 피드백):
- 사용자가 직접 준 데이터
- 예: 평점(1~5점), 좋아요/싫어요, 리뷰

Implicit (암묵적 피드백):
- 행동에서 추출한 데이터
- 예: 클릭, 시청 시간, 구매 여부, 스크롤
- 실무에서 더 많이 사용 (데이터가 풍부)
```

### CF의 장단점

**장점:**

```
✅ 아이템 정보 없이도 작동 (메타데이터 불필요)
✅ 새로운 패턴 발견 가능
✅ 구현이 비교적 간단
```

**단점 (한계점):**

```
❌ Cold Start 문제
   → 신규 사용자/아이템은 추천 불가
   → 평점이 없으면 유사도 계산 불가

❌ Sparsity 문제
   → 대부분 빈칸 (95% 이상)
   → 유사도 계산이 부정확해질 수 있음

❌ Scalability 문제
   → 사용자/아이템 많아지면 계산량 폭증
   → 100만 × 100만 행렬은 현실적으로 불가능
```

---

## Ch1-03. CF 예제 실습 (21:01)

### 실습 데이터셋

```
MovieLens 100K
- 943명의 사용자
- 1,682개의 영화
- 100,000개의 평점
- Sparsity: 약 93.7%
```

### 핵심 구현 단계

#### 1. User-Item Matrix 생성

```python
import pandas as pd

# ratings.csv: user_id, movie_id, rating
matrix = df.pivot_table(
    index='user_id',
    columns='movie_id',
    values='rating'
)

# 결과:
#        movie1  movie2  movie3  ...
# user1    5.0     NaN     4.0
# user2    NaN     3.0     NaN
```

#### 2. 유사도 계산

```python
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

# NaN을 0으로 채우고 희소 행렬로 변환 (메모리 절약)
matrix_sparse = csr_matrix(matrix.fillna(0))

# 사용자 간 유사도 계산
user_similarity = cosine_similarity(matrix_sparse)
# 결과: 943 × 943 행렬
```

#### 3. 평점 예측 (가중 평균)

```python
def predict_rating(user_id, movie_id):
    # 해당 영화를 본 사용자들 찾기
    similar_users = user_similarity[user_id]
    movie_ratings = matrix[movie_id]

    # 유사도 × 평점의 가중 평균
    numerator = (similar_users * movie_ratings).sum()
    denominator = similar_users.sum()

    return numerator / denominator
```

#### 4. Top-K 추천

```python
def recommend(user_id, top_k=5):
    # 아직 안 본 영화들
    unwatched = matrix.loc[user_id].isna()
    unwatched_movies = unwatched[unwatched].index

    # 각 영화의 예측 평점 계산
    predictions = []
    for movie_id in unwatched_movies:
        pred = predict_rating(user_id, movie_id)
        predictions.append((movie_id, pred))

    # 평점 높은 순으로 정렬
    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions[:top_k]
```

### 실습 결과

```
User 1에 대한 추천 (Top 5):
1. 영화 787  (예측 평점: 5.0)
2. 영화 989  (예측 평점: 5.0)
3. 영화 1830 (예측 평점: 5.0)
4. 영화 3172 (예측 평점: 5.0)
5. 영화 3233 (예측 평점: 5.0)

성능 평가:
- RMSE: 약 0.95
- Accuracy: 약 38.2%
```

---

## 백엔드 개발자 관점

### CF vs DB JOIN

```
CF 유사도 계산
= SQL의 Self JOIN + 집계 함수

SELECT u2.movie_id, AVG(u2.rating)
FROM ratings u1
JOIN ratings u2 ON u1.user_id = u2.user_id
WHERE u1.user_id = 1
  AND u2.movie_id NOT IN (본 영화들)
GROUP BY u2.movie_id
ORDER BY AVG(u2.rating) DESC;

→ 하지만 이건 너무 느림!
→ 그래서 미리 계산한 유사도를 캐싱
```

### 실무 구조

```
오프라인 (배치):
- 매일 밤 유사도 행렬 재계산
- Redis/DB에 저장

온라인 (API):
- 캐시된 유사도로 빠르게 추천
- GET /recommend/{user_id}
```

### Sparse Matrix → 메모리 최적화

```
일반 행렬:
943 × 1682 × 8 bytes = 약 12MB

희소 행렬 (csr_matrix):
실제 값만 저장 = 약 1MB

→ 10배 이상 메모리 절약!
```

---

## 핵심 질문 3개

### Q1. User-based vs Item-based, 실무에서 뭘 쓰나?

**A:** Item-based를 더 많이 씀.

```
이유:
1. 사용자는 계속 늘어나지만 아이템은 상대적으로 안정적
2. 아이템 간 유사도는 덜 변함 (매일 재계산 안 해도 됨)
3. "이 영화 본 사람은 저 영화도 봤습니다" 설명이 직관적
```

### Q2. Cold Start 문제 어떻게 해결?

**A:** Hybrid 방식 사용

```
신규 사용자/아이템:
→ Content-based로 추천 (메타데이터 활용)
→ 인기순 추천 (Most Popular)
→ 평점 몇 개 쌓이면 CF로 전환
```

### Q3. 실시간으로 어떻게 추천하나? 계산이 너무 오래 걸리는데?

**A:** 사전 계산 + 캐싱

```
배치 (매일 밤):
- 유사도 행렬 계산
- Top-K 추천 미리 계산
- Redis에 저장

실시간 (API 호출):
- Redis에서 바로 조회
- 응답 시간: < 50ms
```

---

## 한 줄 요약

> CF = 비슷한 사람/아이템 찾아서 빈칸 채우기, 코사인 유사도가 핵심!

---

## 다음 강의 (Ch2)

```
Ch2에서 배울 것:
- Matrix Factorization (MF)
- SVD, ALS
- KNN
- Neural Collaborative Filtering (NCF)

→ CF보다 성능 좋은 고급 기법들
→ 38% → 55~70%로 성능 향상
```

---

**Status**: ✅ 완료  
**Next**: Ch2 - Matrix Factorization & KNN
