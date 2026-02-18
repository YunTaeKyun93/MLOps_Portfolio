# Day 8 - FastAPI + Docker

> **목표:** Day 7 CF 모델을 FastAPI로 서빙 + Docker 컨테이너화  
> **핵심:** BentoML → FastAPI 전환 + Path/Query Parameter + Docker 배포

---

## 학습 목표

- [x] FastAPI 기본 구조 이해
- [x] BentoML → FastAPI 전환
- [x] Path Parameter / Query Parameter 사용
- [x] lifespan으로 서버 시작 시 모델 로드
- [x] Dockerfile 작성 (레이어 캐싱 최적화)
- [x] Docker 빌드 & 실행
- [x] GET /recommend/{user_id} 구현 ✅

---

## 왜 FastAPI로 전환했는가

### BentoML vs FastAPI

```
BentoML (Day 7)
✅ ML 모델 패키징 자동화
✅ bentoml build → containerize 간편
❌ 라우팅이 상대적으로 제한적

FastAPI (Day 8)
✅ 더 유연한 라우팅 (Path/Query Parameter)
✅ NestJS와 구조 거의 동일 (백엔드 개발자에게 친숙)
✅ 범용 API 서버 (ML 외에도 사용 가능)
✅ 실무에서 더 많이 사용
```

**실무에서는:**
- FastAPI로 API 서버 구축
- BentoML은 모델 패키징 도구로 활용
- 둘을 조합해서 사용하는 경우도 많음

---

## FastAPI 핵심 개념

### 1. lifespan - 서버 시작/종료 처리

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시
    print("모델 로딩 중...")
    model_store["matrix"] = pickle.load(...)
    
    yield  # 서버 실행
    
    # 서버 종료 시
    model_store.clear()
```

**백엔드 관점:**
- NestJS의 `onModuleInit()` / `onModuleDestroy()`
- 무거운 pkl 파일을 서버 시작할 때 1번만 로드
- 이후 요청은 메모리에서 바로 참조 (빠름!)

### 2. Pydantic BaseModel (DTO)

```python
class PredictRequest(BaseModel):
    user_id: int
    movie_id: int
```

NestJS의 DTO와 완전히 동일:
```typescript
class PredictDto {
  @IsInt() user_id: number;
  @IsInt() movie_id: number;
}
```

자동으로:
- 타입 검증
- Swagger 문서 생성

### 3. Path / Query Parameter

```python
@app.get("/recommend/{user_id}")
def recommend(user_id: int, top_k: int = 5):
    ...
```

```
/recommend/1?top_k=10
           ↑       ↑
      Path Param  Query Param
```

NestJS 비교:
```typescript
@Get('recommend/:userId')
recommend(
  @Param('userId') userId: number,
  @Query('topK') topK: number = 5
) {}
```

---

## Dockerfile 설계

### 레이어 캐싱 최적화

```dockerfile
# 1단계: requirements.txt 먼저 복사
COPY requirements.txt .
RUN pip install -r requirements.txt
# → 코드 변경해도 이 레이어는 캐시 사용 (빠름!)

# 2단계: 소스 코드는 나중에 복사
COPY src/ ./src/
# → 코드 수정 시 이 레이어부터만 다시 빌드

# 3단계: 모델 파일 복사
COPY outputs/*.pkl ./outputs/
```

**왜 이 순서냐면:**
- `pip install`이 제일 무거운 연산
- 코드는 자주 바뀌지만 패키지는 드물게 바뀜
- 자주 바뀌는 것을 나중에 복사 → 캐시 효율 극대화

### --host 0.0.0.0의 중요성

```dockerfile
# ❌ 틀린 방법
CMD ["uvicorn", "src.service:app"]
# 기본값 --host 127.0.0.1
# → 컨테이너 내부에서만 접근 가능

# ✅ 맞는 방법
CMD ["uvicorn", "src.service:app", "--host", "0.0.0.0"]
# → 외부(호스트)에서 접근 가능
```

---

## 실행 방법

```bash
# 1. 패키지 설치
pip install fastapi uvicorn pandas numpy scikit-learn

# 2. 로컬 테스트
uvicorn src.service:app --reload

# 3. Docker 빌드
docker build -t cf-api .

# 4. Docker 실행
docker run -p 8000:8000 cf-api
```

---

## API 테스트

### Swagger UI
```
http://localhost:8000/docs
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Predict
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "movie_id": 1193}'
```

### Recommend (핵심!)
```bash
curl http://localhost:8000/recommend/1?top_k=5
```

응답:
```json
{
  "user_id": 1,
  "recommendations": [
    {"movie_id": 787, "predicted_rating": 5.0},
    {"movie_id": 989, "predicted_rating": 5.0},
    ...
  ]
}
```

---

## 파일 구조

```
day8-fastapi/
├── notes/
│   ├── lecture_notes.md
│   └── practice_notes.md
├── src/
│   ├── service.py         # FastAPI 서버
│   └── service_easy.py    # 주석 많은 버전
├── outputs/
│   ├── user_item_matrix.pkl  (170MB, git 제외)
│   └── user_similarity.pkl   (278MB, git 제외)
├── Dockerfile
├── requirements.txt
└── README.md              # 이 파일
```

---

## 백엔드 개발자 관점 비교

| FastAPI | NestJS |
|---------|--------|
| @app.get() | @Get() |
| @app.post() | @Post() |
| BaseModel | DTO |
| lifespan | onModuleInit() |
| Path Parameter | @Param() |
| Query Parameter | @Query() |
| HTTPException | NotFoundException |
| Depends() | @Injectable() |

---

## 다음 단계

- Day 9: MLOps 개념 정리
- Day 10: Docker multi-stage build 최적화
- Day 13~: Kubernetes 배포
- Day 20~: AWS ECS 배포

---

## 참고

- Day 7: CF 모델 학습 + BentoML 서빙
- Day 8: FastAPI + Docker (현재)
- FastAPI 공식 문서: https://fastapi.tiangolo.com/