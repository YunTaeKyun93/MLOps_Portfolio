# Day 8 - FastAPI + Docker 실습 노트

> 실습 완료 기준으로 작성

---

## 실습 환경

- OS: Windows
- Python 버전: 3.11
- Docker: Docker Desktop
- FastAPI: 0.104+
- Uvicorn: 0.24+

---

## 실습 흐름

### 1단계 - Day 7 pkl 파일 복사

Day 8에서 Day 7 모델 재사용:

```bash
# day8-fastapi/outputs 폴더 생성
mkdir outputs

# Day 7 pkl 파일 복사
cp ../day7-cf-recommender/outputs/*.pkl ./outputs/
```

pkl 파일:
- `user_item_matrix.pkl` (170MB)
- `user_similarity.pkl` (278MB)

### 2단계 - FastAPI service.py 작성

BentoML → FastAPI 전환 핵심 차이:

```python
# BentoML (Day 7)
@bentoml.service
class CFRecommender:
    @bentoml.api
    def predict(self, request: dict) -> dict:
        ...

# FastAPI (Day 8)
@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    ...
```

**추가된 것:**
- `lifespan` - 서버 시작 시 pkl 로드
- Path Parameter - `/recommend/{user_id}`
- Query Parameter - `?top_k=5`
- HTTPException - 404 에러 처리

### 3단계 - 로컬 테스트

```bash
pip install fastapi uvicorn
uvicorn src.service:app --reload
```

테스트:
```
http://localhost:8000/docs       ← Swagger UI
http://localhost:8000/health     ← 상태 확인
http://localhost:8000/recommend/1?top_k=5
```

결과:
```json
{
  "user_id": 1,
  "recommendations": [
    {"movie_id": 787, "predicted_rating": 5.0},
    ...
  ]
}
```

### 4단계 - Dockerfile 작성

핵심 포인트:

```dockerfile
# 1. requirements.txt 먼저 복사 (캐싱 최적화)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2. 소스 코드는 나중에 복사
COPY src/ ./src/

# 3. pkl 파일 복사
COPY outputs/*.pkl ./outputs/

# 4. 외부 접근 허용!
CMD ["uvicorn", "src.service:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5단계 - Docker 빌드 & 실행

```bash
docker build -t cf-api .
docker run -p 8000:8000 cf-api
```

---

## 막혔던 부분 & 해결 방법

### 1. pkl 파일 경로 에러

```python
# ❌ 문제 코드
OUTPUT_DIR = os.path.join(os.path.dirname(BASE_DIR), "outputs")
# → "/outputs" (루트에서 찾음)

# ✅ 해결
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
# → "/app/outputs" (올바른 경로)
```

**원인:**
```
BASE_DIR = /app
dirname(BASE_DIR) = /  ← 한 단계 더 올라가서 루트가 됨!
join(BASE_DIR, "outputs") = /app/outputs ✅
```

### 2. --host 0.0.0.0 누락

Docker 컨테이너 내부에서만 접근 가능한 문제.

```dockerfile
# ❌ 기본값 (127.0.0.1)
CMD ["uvicorn", "src.service:app"]

# ✅ 외부 접근 허용
CMD ["uvicorn", "src.service:app", "--host", "0.0.0.0"]
```

### 3. 로컬 uvicorn과 Docker 동시 실행

8000 포트가 이미 사용 중인 에러.

**해결:**
로컬 uvicorn 프로세스 종료 (Ctrl+C) 후 Docker 실행.

---

## 새로 알게 된 것

### FastAPI vs BentoML

```
BentoML
- ML 모델 특화
- 자동 패키징 강력
- Bento 빌드 → 배포 간편

FastAPI
- 범용 API 서버
- 더 유연한 라우팅
- NestJS랑 구조 거의 동일
- 실무에서 더 많이 씀
```

### Dockerfile 레이어 캐싱

```
requirements.txt 먼저 복사
→ pip install (무거운 연산)
→ 코드는 나중에 복사

코드 수정 시:
→ pip install 레이어는 캐시 사용 (빠름!)
→ 코드 레이어만 다시 빌드
```

NestJS의 `node_modules` 캐싱과 동일한 전략.

### Path / Query Parameter

```python
@app.get("/recommend/{user_id}")
def recommend(user_id: int, top_k: int = 5):
    ...
```

```
/recommend/1?top_k=10
           ↑       ↑
      Path       Query
```

NestJS:
```typescript
@Get('recommend/:userId')
recommend(
  @Param('userId') userId: number,
  @Query('topK') topK: number = 5
) {}
```

완전히 동일한 개념!

---

## API 테스트 결과

### Health Check
```bash
curl http://localhost:8000/health
```
```json
{"status": "ok"}
```

### Predict
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "movie_id": 1193}'
```
```json
{
  "user_id": 1,
  "movie_id": 1193,
  "predicted_rating": 4.41,
  "rounded_rating": 4
}
```

### Recommend (핵심!)
```bash
curl http://localhost:8000/recommend/1?top_k=5
```
```json
{
  "user_id": 1,
  "recommendations": [
    {"movie_id": 787, "predicted_rating": 5.0},
    {"movie_id": 989, "predicted_rating": 5.0},
    {"movie_id": 1830, "predicted_rating": 5.0},
    {"movie_id": 3172, "predicted_rating": 5.0},
    {"movie_id": 3233, "predicted_rating": 5.0}
  ]
}
```

---

## 폴더 구조

```
day8-fastapi/
├── notes/
│   ├── lecture_notes.md
│   └── practice_notes.md  ← 이 파일
├── src/
│   ├── service.py         ← FastAPI 서버
│   └── service_easy.py    ← 주석 많은 버전
├── outputs/
│   ├── user_item_matrix.pkl  (170MB, git 제외)
│   └── user_similarity.pkl   (278MB, git 제외)
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 다음 할 것

- [ ] Docker Hub에 이미지 푸시
- [ ] AWS ECS 배포 (Day 20~)
- [ ] CI/CD 파이프라인 (GitHub Actions)
- [ ] Kubernetes 배포 (Day 13~)