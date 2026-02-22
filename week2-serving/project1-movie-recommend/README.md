# 🎬 Movie Recommendation API

Collaborative Filtering 기반 영화 추천 시스템을 FastAPI로 서빙하고 Docker로 컨테이너화한 프로젝트

##  프로젝트 통합 배경

MLOps 학습 과정에서 Day 7~11에 걸쳐 단계별로 개발한 내용을 하나의 프로젝트로 통합했다.

- **Day 7**: MovieLens 데이터로 CF 모델 학습 (user_item_matrix, user_similarity)
- **Day 8~9**: FastAPI로 추천 API 서빙 (`/predict`, `/recommend`)
- **Day 10**: 환경 관리 툴 + Container 이론 학습
- **Day 11**: Docker 최적화 (Health Check), pytest 테스트 작성, Docker Compose 구성

학습 기록은 `week2-serving/day7~11` 폴더에 그대로 남겨두고, 완성된 프로젝트만 별도로 통합했다.

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| API 서버 | FastAPI, Uvicorn |
| ML | scikit-learn (cosine similarity), pandas |
| 데이터 | MovieLens 100K |
| 인프라 | Docker, Docker Compose |
| 테스트 | pytest |

## 아키텍처

```
클라이언트
    ↓
FastAPI (8000)
    ↓
Collaborative Filtering 모델
(user_item_matrix.pkl + user_similarity.pkl)
```

## 📁 프로젝트 구조

```
project1-movie-recommend/
├── src/
│   ├── train.py          # CF 모델 학습
│   └── service.py        # FastAPI 앱
├── outputs/
│   ├── user_item_matrix.pkl
│   └── user_similarity.pkl
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── test_service.py
└── README.md
```

## 실행 방법

### Docker Compose (권장)
```bash
docker compose up --build
```

### 로컬 실행
```bash
pip install -r requirements.txt
uvicorn src.service:app --host 0.0.0.0 --port 8000
```

## 📡 API 명세

### GET /health
서버 상태 확인
```json
{
  "status": "OK",
  "model_loaded": true
}
```

### POST /predict
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

### GET /recommend/{user_id}?top_k=5
유저에게 영화 top_k개 추천

**Response**
```json
{
  "user_id": 1,
  "recommendations": [
    {"movie_id": 318, "predicted_rating": 4.85},
    {"movie_id": 858, "predicted_rating": 4.72}
  ]
}
```

## 테스트

```bash
pytest test_service.py -v
```

```
test_health_check           PASSED
test_predict_valid          PASSED
test_predict_unknown_user   PASSED
test_predict_unknown_movie  PASSED
test_predict_invalid_body   PASSED
test_recommend_valid        PASSED
test_recommend_top_k        PASSED
test_recommend_sorted       PASSED
test_recommend_unknown_user PASSED

9 passed in 4.24s
```

## 주요 구현 포인트

- **lifespan**: 서버 시작 시 pkl 모델 로드, 종료 시 메모리 해제
- **Health Check**: Docker 컨테이너 상태 모니터링 (`/health` 엔드포인트)
- **Cold Start 대응**: `start_period: 15s` 설정으로 모델 로딩 시간 확보
- **미시청 필터링**: 유저가 이미 본 영화는 추천에서 제외