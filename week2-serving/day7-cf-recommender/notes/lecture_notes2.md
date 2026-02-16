# Day 7 - Ch2. Matrix Factorization & KNN 강의노트
> Week 2 | MLOps 서빙/배포 파트
> 강의 수준: 이론 이해 + 구조 파악 위주 (수식 증명 ❌)

---

## Ch2-01. 행렬 분해의 기본 원리 (26:47) 🟡

### CF와 MF의 차이

```
CF (어제)
→ 비슷한 사람 찾아서 평점 빌려오기
→ 유사도 계산이 핵심
→ 학습(training) 없음

MF (오늘)
→ 행렬 자체를 분해해서 숨겨진 특성을 학습
→ 학습(training)이 핵심
→ CF보다 성능 좋음 (38% → 55~65%)
```

### Matrix Factorization 구조

```
원본 행렬 (Sparse, NaN 투성이)
         ↓ 분해
User Latent Matrix  ×  Item Latent Matrix
(6040 × 10)            (3706 × 10)
         ↓ 내적(dot product)
예측 행렬 (Dense, 빈칸 없음)
```

### Latent Factor

- 행렬을 분해했을 때 나오는 숨겨진 기준 축
- 예: 액션 선호도, 로맨스 선호도, 배우 선호도 등
- **이름은 모델이 알아서 학습** → 우리가 붙이는 게 아님
- num_features = 10 → Latent Factor 10개

### 학습 과정 (SGD)

```python
# 핵심 흐름
prediction = np.dot(user_features[user_id], movie_features[movie_id])  # 내적으로 예측
error = rating - prediction                                              # 오차 계산

# 오차 줄이는 방향으로 벡터 업데이트
user_features[user_id] += learning_rate * (error * movie_features[movie_id] - regularization * user_features[user_id])
movie_features[movie_id] += learning_rate * (error * user_features[user_id] - regularization * movie_features[movie_id])
```

```
epoch 20번 × 98만 건 순회
→ 틀릴 때마다 조금씩 수정
→ 점점 예측이 정확해짐
```

### Regularization

```
L1 Norm  → 절대값 합 → 일부 파라미터를 0으로 만듦 (파라미터 비활성화)
L2 Norm  → 제곱합   → 파라미터가 너무 커지는 것 방지 (과적합 방지)

코드에서: - regularization * user_features[user_id]
→ 숫자가 커질수록 더 많이 억제 = L2
```

### 실무에서 네 역할
```
ML팀  → 모델 학습, 벡터(임베딩) 생성
나    → 벡터를 DB에 저장
       추론 API 작성
       캐싱 전략 설계
       대용량 요청 처리
```

---

## Ch2-02. SVD (15:29) 🟡

### 한 줄 요약
> 행렬을 U × Σ × Vᵀ 로 분해해서 중요한 것만 남기는 압축 기법

### 핵심 개념

```
전체 특이값 중 k개만 남김
→ 차원 축소
→ 노이즈 제거
→ 압축

k 크면  → 정확하지만 느림
k 작으면 → 빠르지만 정보 손실
```

### 실무 활용
- PCA의 기반 기술
- 이미지 압축
- 텍스트 분석 (LSA)
- 라이브러리로 바로 사용 (`scipy.linalg.svd`)

---

## Ch2-03. ALS (13:38) 🟡

### 한 줄 요약
> SGD 대신 User/Item을 번갈아가며 최적화하는 방법

### SGD vs ALS

```
SGD
→ 모든 파라미터 동시에 조금씩 업데이트
→ 구현 간단
→ 소규모에 적합

ALS
→ User 고정 → Item 최적화
→ Item 고정 → User 최적화
→ 번갈아 반복
→ 병렬 처리 가능 → 대규모에 강함
→ Spark MLlib에서 많이 사용
```

### 실무 맥락
- 수백만 사용자 × 수백만 아이템 규모
- Netflix, Spotify 같은 대형 서비스
- Spark + ALS 조합이 업계 표준

---

## Ch2-04. KNN (9:47) 🔴

### 한 줄 요약
> 벡터 간 거리를 계산해서 가장 가까운 것을 찾는 것

### 유사도 종류

```
Cosine Similarity  → 방향이 얼마나 같은가 (0~1)
                     크기 달라도 비교 가능
                     텍스트, 임베딩에 주로 사용 ← 실무에서 많이 씀

Euclidean Distance → 실제 거리 (좌표 기반)
                     크기에 영향받음
```

### KNN → ANN 확장 (중요!)

```
KNN (정확한 탐색)
→ 데이터 많아지면 너무 느림
→ 100만 벡터 전부 비교 = 실시간 불가

ANN (근사 최근접 탐색)
→ 조금 틀려도 되니까 빠르게
→ 실서비스에서는 전부 ANN 사용
```

### 실무 연결 (진짜 중요!)

```
KNN 이해
  ↓
FAISS (Facebook AI 벡터 검색 라이브러리)
  ↓
Milvus / Pinecone (벡터 DB)
  ↓
LLM RAG ("질문과 비슷한 문서 찾기")

→ AI 백엔드 핵심 기술 스택
```

---

## Ch2-05. Neural Collaborative Filtering (🟡)

### 한 줄 요약
> MF의 내적 대신 MLP(딥러닝)로 더 복잡한 패턴 학습

### MF vs NCF

```
MF
→ user벡터 · item벡터 = 점수
→ 내적 (선형) = 단순한 관계만 학습

NCF
→ user벡터 + item벡터 → MLP 통과 → 점수
→ 비선형 = 복잡한 패턴도 학습
→ 성능은 좋지만 학습 비용 큼
```

### 구조

```
User 임베딩 ─┐
              ├→ concat → MLP(여러 레이어) → 점수 예측
Item 임베딩 ─┘
```

### LLM과의 연결

```
NCF 구조  =  임베딩 → 신경망 → 출력
LLM 구조  =  토큰 임베딩 → Transformer → 출력

근본 구조가 같음!
```

---

## Ch2 전체 정리

```
MF  → 벡터(임베딩) 만들기        ← 임베딩의 출발점
KNN → 벡터 검색하기              ← RAG, 벡터DB 직결 🔴
NCF → 딥러닝으로 확장            ← LLM과 같은 구조
ALS → 대규모로 확장              ← Spark 환경
SVD → 차원 줄이기                ← 압축 도구
```

### 오늘 핵심 한 줄
> 추천 시스템 = 벡터 공간 + 유사도 + 반복 최적화
> 이게 곧 임베딩 → RAG → LLM의 기반

### 성능 비교
```
랜덤 예측   → 20%
전체 평균   → 28%
CF          → 38%   (어제 구현)
MF / SVD   → 55~65%
NCF         → 70%+
```