# Day 8 - FastAPI 서빙 + Docker 컨테이너화 강의노트
> Week 2 | MLOps 서빙/배포 파트  
> 강의: [B] Part2 Ch3-01~02

---

## Ch3-01. FastAPI로 모델 서빙 (16:29) 🔴

**핵심 개념**

FastAPI는 Python 기반 웹 프레임워크로, ML 모델을 API로 서빙하는 데 최적화되어 있음.

```
BentoML  → ML 모델 패키징/배포 특화, 자동화 강력
FastAPI  → 범용 API 서버, 더 유연한 라우팅, 실무에서 많이 씀
```

**백엔드 연결**

```
FastAPI           NestJS
─────────────────────────────
@app.get()        @Get()
@app.post()       @Post()
BaseModel         DTO (class CreateUserDto)
Depends()         @Injectable()
Path Parameter    @Param('id')
Query Parameter   @Query()
HTTPException     NotFoundException
```

**왜 FastAPI를 쓰냐면**

1. **자동 문서화** - Swagger UI 자동 생성 (`/docs`)
2. **타입 검증** - Pydantic으로 요청/응답 자동 검증
3. **비동기 지원** - async/await 네이티브 지원
4. **성능** - Starlette 기반, Node.js급 속도
5. **범용성** - ML 외에도 모든 백엔드 API 가능

**lifespan - 서버 시작/종료 처리**

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

백엔드 관점: NestJS의 `onModuleInit()` / `onModuleDestroy()`와 동일.
무거운 pkl 파일을 서버 시작할 때 1번만 로드 → 이후 요청은 메모리에서 바로 참조.

**Pydantic BaseModel**

```python
class PredictRequest(BaseModel):
    user_id: int
    movie_id: int
```

이게 바로 NestJS의 DTO:
```typescript
class PredictDto {
  @IsInt() user_id: number;
  @IsInt() movie_id: number;
}
```

자동으로 타입 검증 + Swagger 문서 생성.

**Path / Query Parameter**

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

---

### [B] Part2 Ch3-02. FastAPI 앱 컨테이너화 (13:48) 🔴

**Dockerfile 구조**

```dockerfile
FROM python:3.11-slim           # Base Image
WORKDIR /app                    # 작업 디렉토리

COPY requirements.txt .         # 패키지 목록 먼저 복사
RUN pip install -r requirements.txt  # 설치 (레이어 캐싱)

COPY src/ ./src/                # 소스 코드 복사
COPY outputs/*.pkl ./outputs/   # 모델 파일 복사

EXPOSE 8000                     # 포트 노출
CMD ["uvicorn", "src.service:app", "--host", "0.0.0.0", "--port", "8000"]
```

**레이어 캐싱 최적화**

```
requirements.txt 먼저 복사 → pip install
→ 코드 변경해도 패키지는 재설치 안 함!

src/ 나중에 복사
→ 코드 수정 시 이 레이어부터만 다시 빌드
```

백엔드 관점: `package.json` 먼저 복사 → `npm install` → 소스 복사 순서와 동일.

**--host 0.0.0.0의 중요성**

```python
# ❌ 틀린 방법
CMD ["uvicorn", "src.service:app"]
# 기본값 --host 127.0.0.1
# → 컨테이너 내부에서만 접근 가능

# ✅ 맞는 방법
CMD ["uvicorn", "src.service:app", "--host", "0.0.0.0"]
# → 외부(호스트)에서 접근 가능
```

**Docker 빌드 & 실행**

```bash
# 빌드
docker build -t cf-api .

# 실행
docker run -p 8000:8000 cf-api
#          호스트:컨테이너
```

---

## 핵심 한 줄 요약

```
FastAPI = NestJS처럼 쓰는 Python API 서버
Docker  = 어디서나 똑같이 실행되는 패키지
```

---

## 백엔드 개발자 관점 정리

| ML 개념 | 백엔드 개념 |
|---------|-----------|
| FastAPI service.py | NestJS Controller + Service |
| Pydantic BaseModel | DTO |
| lifespan | onModuleInit() |
| Path/Query Parameter | @Param() / @Query() |
| Dockerfile | 실행 환경 정의 |
| docker build | npm run build |
| docker run | 배포된 서버 실행 |
| --host 0.0.0.0 | 외부 접근 허용 설정 |

---

## 다음 할 것 (Day 9~)

- AWS ECS 배포 (강의 Ch3-03~05)
- CI/CD 파이프라인 (GitHub Actions)
- Kubernetes (Day 13~)