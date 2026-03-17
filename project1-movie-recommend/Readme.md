# 영화 추천 시스템 (Collaborative Filtering)

MovieLens 1M 데이터를 기반으로 한 User-Based Collaborative Filtering 추천 API.  
모델 학습부터 FastAPI 서빙, Docker 컨테이너화, AWS ECR 배포, GitHub Actions CI/CD까지 E2E 파이프라인 구현.

---

## 아키텍처

```
[MovieLens 1M 데이터]
        ↓
[train.py] User-Item Matrix 생성 → Cosine Similarity 계산
        ↓
[outputs/*.pkl] user_item_matrix.pkl, user_similarity.pkl
        ↓
[FastAPI 서버] 앱 시작 시 모델 로드 (lifespan)
        ↓
[Docker 이미지] python:3.11-slim + HEALTHCHECK
        ↓
[GitHub Actions] pytest → Docker build (linux/amd64) → ECR push
        ↓
[AWS ECR] 947632012584.dkr.ecr.ap-northeast-2.amazonaws.com/movie-recommend
```

---

## 기술 스택

| 분류     | 기술                                                  |
| -------- | ----------------------------------------------------- |
| ML       | scikit-learn (cosine_similarity), scipy (csr_matrix)  |
| 서빙     | FastAPI, Uvicorn, Pydantic                            |
| 컨테이너 | Docker (python:3.11-slim), HEALTHCHECK                |
| CI/CD    | GitHub Actions, AWS ECR                               |
| 테스트   | pytest, FastAPI TestClient                            |
| 데이터   | MovieLens 1M (100만 건, 사용자 6,040명, 영화 3,706개) |

---

## API 엔드포인트

### `GET /health`

서버 및 모델 로드 상태 확인

```json
{
  "status": "OK",
  "model_loaded": true
}
```

### `POST /predict`

특정 유저의 특정 영화 예측 평점 반환

**Request**

```json
{
  "user_id": 1,
  "movie_id": 1193
}
```

**Response**

```json
{
  "user_id": 1,
  "movie_id": 1193,
  "predicted_rating": 4.23,
  "rounded_rating": 4
}
```

**예외 처리**

- 미지원 user_id / movie_id → 기본값 `3.0` 반환 (콜드 스타트 처리)
- 잘못된 타입 입력 → `422 Unprocessable Entity`

### `GET /recommend/{user_id}?top_k=5`

유저가 아직 보지 않은 영화 중 예측 평점 상위 K개 추천

**Response**

```json
{
  "user_id": 1,
  "recommendations": [
    { "movie_id": 318, "predicted_rating": 4.87 },
    { "movie_id": 858, "predicted_rating": 4.82 }
  ]
}
```

**예외 처리**

- 존재하지 않는 user_id → `404 Not Found`

---

## 모델 상세

### 알고리즘: User-Based Collaborative Filtering

```
1. User-Item Matrix 생성
   - 행: user_id, 열: movie_id, 값: rating (1~5)
   - NaN: 해당 유저가 해당 영화를 평가하지 않음
   - Sparsity: ~95.6% (MovieLens 1M 기준)

2. Cosine Similarity 계산
   - csr_matrix(희소행렬)로 변환 후 계산 (메모리 최적화)
   - 결과: 6040×6040 유저 간 유사도 행렬

3. 예측 평점 계산
   - 해당 영화를 평가한 유저들의 평점 × 유사도 가중 평균
   - 공식: Σ(sim_i × rating_i) / Σ(sim_i)
```

### 모델 성능

- **Accuracy**: 약 27% (예측 평점을 반올림 후 실제 평점과 비교)
- **평가 방법**: test split 2% (약 2만 건)
- **저장 기준**: 이전 best_acc보다 높을 때만 모델 갱신 (`best_acc.txt` 비교)

> Accuracy가 낮아 보이지만, 평점 예측은 분류가 아닌 회귀 문제에 가까움.  
> 반올림 후 정확도보다 RMSE 기준 평가가 더 적합 (다음 개선 목표).

---

## 프로젝트 구조

```
project1-movie-recommend/
├── app/
│   ├── routers/recommend.py   # API 엔드포인트 (NestJS Controller)
│   ├── services/recommend.py  # 비즈니스 로직 - 모델 로드/추론 (NestJS Service)
│   └── schemas/recommend.py   # Request/Response 타입 정의 (NestJS DTO)
├── src/
│   └── train.py               # 모델 학습 스크립트
├── outputs/
│   ├── user_item_matrix.pkl   # User-Item Matrix
│   ├── user_similarity.pkl    # Cosine Similarity Matrix
│   └── best_acc.txt           # 최고 성능 기록
├── main.py                    # FastAPI 앱 진입점 + lifespan 훅
├── Dockerfile                 # 컨테이너 이미지 정의
├── requirements.txt           # 의존성
└── test_service.py            # pytest 테스트 (9개)
```

---

## 실행 방법

### 로컬 실행

```bash
# 1. 모델 학습
python src/train.py

# 2. 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000

# 3. 테스트
pytest test_service.py -v
```

### Docker 실행

```bash
# 빌드
docker build --platform linux/amd64 -t movie-recommend .

# 실행
docker run -p 8000:8000 movie-recommend

# API 확인
curl http://localhost:8000/health
```

---

## CI/CD 파이프라인

```
PR 오픈
  ↓
check job (항상 통과) ← Branch Protection Ruleset 기준
  ↓
test job (project1 경로 변경 시에만 실행)
  ├── pytest 9개 통과
  ├── Docker 빌드 (--platform linux/amd64)  ← M1 Mac → ECS 배포 시 필수
  └── ECR 푸시 ({sha} 태그 + latest 태그)
  ↓
머지 가능
```

**주요 트러블슈팅**

| 문제                              | 원인                                                  | 해결                                               |
| --------------------------------- | ----------------------------------------------------- | -------------------------------------------------- |
| ECS 배포 후 `exec format error`   | M1 Mac(ARM)에서 빌드한 이미지를 ECS(amd64)에 배포     | `--platform linux/amd64` 추가                      |
| CI `check` job 미통과로 머지 불가 | path 필터로 `test` job이 skip되면 Ruleset 조건 미충족 | `check` job을 별도로 분리하여 항상 통과하도록 구성 |
| ECR push 실패                     | IAM 권한 부족                                         | `AmazonEC2ContainerRegistryPowerUser` 정책 추가    |

---

## 개선 예정

- [ ] RMSE 기반 평가 지표로 교체 (현재 Accuracy → 회귀 문제에 부적합)
- [ ] MLflow 연동 (실험 추적 + 모델 레지스트리)
- [ ] 멀티스테이지 Dockerfile (빌더 / 런타임 분리)
- [ ] 콜드 스타트 개선 (인기 기반 Fallback → 단순 3.0 반환 대신)
