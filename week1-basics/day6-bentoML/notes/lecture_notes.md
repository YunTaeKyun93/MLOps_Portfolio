# Day 6 강의 노트 - BentoML을 통한 모델 서빙

> Ch 7-03 BentoML 서빙 (강의 대신 Titanic 기준 직접 실습으로 대체)

---

## Ch 7-01 모델 배포 전략 (복습)

### 배포 환경 3가지

| 환경       | 특징                         | 사용 기술                      |
| ---------- | ---------------------------- | ------------------------------ |
| On-premise | 자체 서버실, GPU 직접 운용   | CUDA, K8s 직접 구축            |
| Cloud      | 표준 방식, 자원 유연성       | AWS SageMaker, GCP Vertex AI   |
| Edge       | 모바일/임베디드, 경량화 필수 | ONNX, TensorLite, Quantization |

### 배포 방식 3가지

```
Online Serving  → 요청 즉시 응답 (Request 기반)
                  예: 챗봇, 결제 시스템

Batch Serving   → 모아서 한 번에 처리
                  예: 새벽 추천 시스템, 통계 집계

Streaming       → 요청 없이 데이터가 계속 흘러옴 (이벤트 기반)
                  예: Kafka, 실시간 로그 분석
```

**핵심 차이:**

```
Online   = Request 기반  (클라이언트가 요청해야 처리)
Streaming = 이벤트 기반  (데이터가 알아서 들어옴)
```

### 서빙 아키텍처

```
클라이언트 → API Gateway → Load Balancer → Model Server (컨테이너 클러스터)
                                ↓
                          라운드로빈으로 요청 분산
```

### 배포 고려사항

```
Latency      = 네트워크 + API처리 + 모델추론 + 후처리
               (모델 크기가 치명적!)

Throughput   = 초당 처리 요청 수

Availability = 서비스 안정성
               99.9% uptime = 연간 8.7시간 다운

비용         = GPU + 트래픽 + 스토리지
               (ML은 GPU 비용이 일반 백엔드보다 훨씬 큼)
```

---

## Ch 7-03 BentoML 서빙

### BentoML이란?

> ML 모델을 위한 API 서버 프레임워크  
> = **"ML 모델을 위한 NestJS"**

### FastAPI vs BentoML

```
FastAPI:
  - 직접 모델 로드 코드 작성
  - 직접 전처리 파이프라인 구성
  - Docker 이미지 직접 작성
  - 버전 관리 없음

BentoML:
  - 모델 저장 → Service 정의 → 끝
  - Swagger UI 자동 생성
  - Docker 이미지 자동 생성 (bentoml build)
  - ModelStore로 버전 관리 내장
  - 배치 처리 내장
```

---

## 핵심 개념

### Runner

```python
runner = bentoml.sklearn.get("titanic_model:latest").to_runner()
```

- **NestJS의 Service 클래스**
- 모델을 실제로 실행하는 단위
- `async_run()` 으로 비동기 추론 지원
- 내부적으로 스레드풀, 배치 처리 자동 관리

### Service

```python
svc = bentoml.Service("titanic_service", runners=[runner])

@svc.api(input=JSON(), output=JSON())
async def predict(input_data) -> dict:
    ...
```

- **NestJS의 Controller**
- `@svc.api` 데코레이터로 엔드포인트 정의
- Swagger UI 자동 생성

### Bento

```bash
bentoml build        # Bento 생성
bentoml containerize # Docker 이미지 변환
```

- 모델 + 코드 + 환경을 하나로 묶은 패키지
- = Docker 이미지 개념

---

## ModelStore

### 개념

```
best_model.pkl     = 로컬 파일 (프로젝트 내부)
BentoML ModelStore = npm global registry (어디서든 접근 가능)
```

### 저장 위치

```
~/.bentoml/models/titanic_model/tmdmbaajss4rhzus/
```

### 주요 명령어

```bash
bentoml models list           # 등록된 모델 목록
bentoml models get titanic_model:latest  # 특정 모델 상세 정보
bentoml models delete titanic_model:태그  # 모델 삭제
```

---

## 전체 서빙 흐름

```
1. 모델 학습 (Day 4)
   └── best_model.pkl 생성

2. ModelStore 등록
   └── bentoml.sklearn.save_model("titanic_model", model)
   └── 버전 태그 자동 생성 (tmdmbaajss4rhzus)

3. service.py 작성
   └── Runner 생성 (모델 실행 엔진)
   └── Service 정의 (API 서버)
   └── 엔드포인트 구현

4. 서버 실행
   └── bentoml serve src/service.py:svc --reload
   └── localhost:3000 (Swagger UI 포함)

5. 예측 요청
   └── curl POST /predict
   └── {"survived": 1, "message": "1 = 생존, 0 = 사망"}
```

---

## 주요 코드 패턴

### DataFrame 변환 이유

```python
features = pd.DataFrame([input_data])
# [input_data]로 감싸는 이유:
# sklearn 모델은 2차원 입력을 기대
# → 행 1개짜리 테이블로 만들어야 함
```

### 컬럼 순서 강제 정렬

```python
features = features[EXPECTED_COLUMNS]
# 이유: 학습 때와 컬럼 순서가 다르면 에러 발생
# ValueError: Feature names must be in the same order as they were in fit.
```

### 비동기 추론

```python
result = await runner.predict.async_run(features)
# BentoML은 async/await 지원
# → 여러 요청을 동시에 처리 가능 (논블로킹)
```

### 결과 캐스팅

```python
int(result[0])
# sklearn predict 결과 = 배열 형태 array([1])
# result[0]으로 첫 번째 값 꺼내고
# JSON에 담기 위해 int()로 캐스팅
```

---

## 현재 단계의 한계

```
로컬 서버의 한계:
  - 터미널 켜있을 때만 동작
  - 내 컴퓨터에서만 접근 가능
  - 서버 재시작 시 수동으로 다시 실행

해결책 (Day 7~8):
  - bentoml build → Bento 패키지 생성
  - bentoml containerize → Docker 이미지 생성
  - 클라우드 배포 → 항상 켜있는 서버
```

---

## 핵심 질문 정리

**Q1. Runner와 Service의 차이는?**

> Runner = 모델 실행 담당 (Service 역할)  
> Service = API 엔드포인트 정의 (Controller 역할)

**Q2. ModelStore를 왜 쓰나?**

> 버전 관리 + 어디서든 접근 + Docker 패키징 자동화

**Q3. 왜 async/await를 쓰나?**

> 여러 요청 동시 처리 가능 (논블로킹)  
> 모델 추론이 느릴 때 다른 요청도 처리할 수 있음

**Q4. 컬럼 순서가 왜 중요한가?**

> sklearn 모델은 학습 때와 정확히 동일한 컬럼 순서를 기대  
> 순서 다르면 ValueError 발생

**Q5. Bento와 Docker의 차이는?**

> Bento = ML 특화 패키지 형식  
> Docker = 범용 컨테이너  
> bentoml containerize 로 Bento → Docker 이미지 변환 가능
