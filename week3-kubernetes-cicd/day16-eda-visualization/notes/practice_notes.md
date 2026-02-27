# Day 16 실습 노트 - 추천 시스템 EDA + 시각화

**날짜**: 2026.02.27
**목표**: MovieLens 데이터로 EDA + 시각화 3개 만들기

---

## 실습 1: 데이터 로딩 및 기본 통계

### 목표

- [x] ratings.dat 로딩
- [x] 기본 통계 확인 (평점 수, 유저 수, 영화 수)

### 핵심 코드

```python
import os
import pandas as pd
import matplotlib.pyplot as plt

# 경로 설정 (어디서 실행해도 안전)
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, '..', 'data', 'ml-1m', 'ratings.dat')
output_path = os.path.join(base_dir, '..', 'outputs')

# 데이터 로딩
ratings = pd.read_csv(
    file_path,
    sep="::",
    engine="python",
    names=["user_id", "movie_id", "rating", "timestamp"]
)

print(f"총 평점 수: {len(ratings):,}")       # 1,000,209
print(f"총 유저 수: {ratings['user_id'].nunique():,}")   # 6,040
print(f"총 영화 수: {ratings['movie_id'].nunique():,}")  # 3,706
```

### 실행 결과

```
총 평점 수: 1,000,209
총 유저 수: 6,040
총 영화 수: 3,706
```

### 백엔드 연결

```python
# os.path.join = Node.js path.join(__dirname, ...)과 동일
# 어디서 실행해도 경로 깨지지 않음
```

---

## 실습 2: 평점 분포 시각화

### 목표

- [x] 1~5점 평점 분포 bar chart
- [x] outputs/ 폴더에 PNG 저장

### 핵심 코드

```python
plt.figure(figsize=(8, 5))
ratings['rating'].value_counts().sort_index().plot(kind='bar', color='steelblue')
plt.title('평점 분포')
plt.xlabel('평점')
plt.ylabel('개수')
plt.tight_layout()
plt.savefig(os.path.join(output_path, 'rating_distribution.png'))
plt.show()
```

### 인사이트

- 4점이 가장 많음 → 유저들이 좋아하는 영화만 평점 남기는 경향
- 1점은 매우 적음 → 극단적 부정 평가는 드묾

---

## 실습 3: 인기 영화 Top 10

### 목표

- [x] 평점 수 기준 인기 영화 Top 10
- [x] bar chart로 시각화

### 핵심 코드

```python
top10 = ratings.groupby('movie_id')['rating'].count() \
               .sort_values(ascending=False) \
               .head(10)

plt.figure(figsize=(10, 6))
top10.plot(kind='bar', color='coral')
plt.title('인기 영화 Top 10 (평점 수 기준)')
plt.xlabel('영화 ID')
plt.ylabel('평점 수')
plt.tight_layout()
plt.savefig(os.path.join(output_path, 'top10_movies.png'))
plt.show()
```

### 인사이트

- 특정 영화에 평점이 집중됨 → 롱테일 분포
- CF 모델이 인기 영화 위주로 추천하는 이유

---

## 실습 4: 유저별 평점 개수 분포

### 목표

- [x] 유저별 평점 개수 histogram
- [x] Cold Start 문제 확인

### 핵심 코드

```python
user_rating_count = ratings.groupby('user_id')['rating'].count()

plt.figure(figsize=(10, 5))
plt.hist(user_rating_count, bins=50, color='mediumseagreen', edgecolor='white')
plt.title('유저별 평점 개수 분포')
plt.xlabel('평점 개수')
plt.ylabel('유저 수')
plt.tight_layout()
plt.savefig(os.path.join(output_path, 'user_rating_distribution.png'))
plt.show()
```

### 인사이트

- 대부분 유저는 평점 적게 남김 → Cold Start 문제
- 일부 헤비유저만 많은 평점 → 추천 정확도 높음
- CF 모델이 신규 유저한테 추천 못 하는 이유가 여기 있음

---

## 🔥 트러블슈팅

| 에러          | 원인                       | 해결                                         |
| ------------- | -------------------------- | -------------------------------------------- |
| 상대경로 오류 | 실행 위치에 따라 경로 깨짐 | `os.path.dirname(__file__)` 로 절대경로 처리 |

---

## ✅ 오늘 완성한 것

- [x] notebooks/eda.py 작성
- [x] rating_distribution.png
- [x] top10_movies.png
- [x] user_rating_distribution.png

---

## 📝 회고

- **배운 것**: groupby는 SQL GROUP BY와 동일. 시각화보다 인사이트 도출이 중요
- **막혔던 부분**: 없음. 흐름 자체는 자연스러웠음
- **내일 연결**: Week 3 마무리 + 블로그 #1 작성 시작

---

git push origin feat/da17-eda-visualization
