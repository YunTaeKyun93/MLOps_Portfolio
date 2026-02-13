# Day 5: Docker 기초

**날짜**: 2026.02.13
**강의**: [B] Part 1 - Ch 8 (도커 및 컨테이너 기술)

---

## 목표

> Day 4에서 만든 best_model.pkl을 Docker로 컨테이너화
> 다음 주 FastAPI 서빙의 기반이 되는 날

| 항목        | 내용                                          |
| ----------- | --------------------------------------------- |
| 핵심        | Dockerfile 작성 → 이미지 빌드 → 컨테이너 실행 |
| 백엔드 관점 | Docker = "내 코드가 어디서든 똑같이 동작"     |
| 다음 연결   | Day 6 FastAPI 서빙 + Docker Compose           |

---

## 진행 상황

### 강의

- [x] 1.  도커 소개 및 기본 개념 (35분)
- [x] 2.  예제 프로그램 도커로 서비스하기 (14분)
- [x] 3.  도커 파일 및 빌드 (18분)
- [x] 4.  실습: 도커 파일 및 빌드 (32분)
- [x] 6.  도커 컴포즈 소개 (30분)
- ~~05. 도커 스웜~~ → Skip (실무에서 K8s로 대체)

### 실습

- [x] 실습 1: Docker 설치 확인 + 기본 명령어
- [x] 실습 2: Dockerfile 작성 + 이미지 빌드 + 컨테이너 실행 성공
- [x] 실습 3: [VS] 이미지 크기 비교 (slim vs full)
- [x] 실습 4: [WHAT IF] COPY 순서 실험
- [x] 실습 5: [WHAT IF] .dockerignore 효과
- [x] 실습 6: [WHY] --no-cache-dir 실험

### 정리

- [x] `notes/lecture_notes.md` 작성
- [x] `notes/practice_notes.md` 작성

---

## 폴더 구조

```
day5-docker/
├── notes/
│   ├── lecture_notes.md
│   └── practice_notes.md
├── outputs/
│   └── best_model.pkl
├── src/
│   └── predict.py
├── .dockerignore
├── Dockerfile
├── Dockerfile.bad          # COPY 순서 실험용
├── requirements.txt
└── README.md
```

---

## 핵심 개념

### Docker 기본

- **Docker vs VM**: VM은 OS 전체 격리(GB, 느림), Docker는 프로세스만 격리(MB, 빠름)
- **Image**: 패키징한 내용물 (붕어빵 틀) → 같은 Image로 Container 여러 개 실행 가능
- **Container**: 실행 중인 프로세스 (붕어빵)
- **Layer 캐시**: 자주 안 바뀌는 것 앞에 배치 → 캐시 유지 → 빌드 속도 절약

### Dockerfile

```dockerfile
FROM python:3.11-slim          # ML 환경 표준 (glibc 호환, alpine ❌)
WORKDIR /app
COPY requirements.txt .        # 자주 안 바뀜 → 앞에!
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src/                # 자주 바뀜 → 뒤에!
COPY outputs ./outputs/
CMD ["python", "src/predict.py"]
```

### Docker Compose

- 여러 컨테이너 한번에 실행 + 의존성 순서 보장 + 환경변수 안전 관리
- `depends_on`: DB 먼저 → 앱 실행 순서 보장
- `volumes`: 컨테이너 꺼져도 데이터 유지

---

## 백엔드 연결

```
Docker Image    = npm 패키지 (빌드 결과물)
Container       = 실행 중인 프로세스
Dockerfile      = package.json + 빌드 스크립트
.dockerignore   = .gitignore
docker-compose  = PM2 ecosystem (여러 서비스 한번에)
Layer 캐시      = npm install 캐시와 동일
volumes         = 디스크 (컨테이너 꺼져도 유지)
.env 분리       = Nest.js .env와 완전히 동일
```

---

## 실습 결과

### [VS] 이미지 크기 비교

| 이미지           | 크기   | 비고                 |
| ---------------- | ------ | -------------------- |
| python:3.11      | 3.19GB | full                 |
| python:3.11-slim | 212MB  | **93% 절감**         |
| titanic-model    | 711MB  | slim + ML 라이브러리 |

### [WHAT IF] COPY 순서 실험

| Dockerfile                   | 재빌드 시간 | 비고                    |
| ---------------------------- | ----------- | ----------------------- |
| 비효율 (COPY . . 먼저)       | 33.156초    | pip install 매번 재실행 |
| 효율 (requirements.txt 먼저) | 0.467초     | **70배 빠름**           |

### [WHY] --no-cache-dir 실험

| 옵션                | 이미지 크기 | 비고           |
| ------------------- | ----------- | -------------- |
| --no-cache-dir 없음 | 853MB       | pip 캐시 포함  |
| --no-cache-dir 있음 | 711MB       | **142MB 절감** |

### [WHAT IF] .dockerignore 효과

- 차이 없음 (711MB → 711MB)
- 이유: 제외 대상 파일이 KB 단위로 작아서 티 안 남
- 실무에서는 GB 단위 data/ 폴더 제외 시 효과 큼

---

## 트러블슈팅

### numpy 버전 충돌 2종

| 에러                            | 원인                         | 해결                  |
| ------------------------------- | ---------------------------- | --------------------- |
| `numpy.dtype size changed`      | requirements.txt 버전 미지정 | numpy==2.4.1 고정     |
| `No module named 'numpy._core'` | numpy 2.0+ 내부 구조 변경    | 로컬 버전 그대로 고정 |

**교훈**:

```
pip freeze | grep -E "pandas|numpy|scikit-learn|joblib"
→ 로컬 버전 확인 후 requirements.txt에 명시적 고정
Docker = 재현성 도구지만, 버전 고정 안 하면 소용없음!
```

---

## 스스로 찾아보기 발견

- **docker dive**: 이미지 레이어별 크기 분석 도구 → Week 9 포트폴리오 최적화 때 활용 예정
- **docker tag**: Docker Hub에 이미지 게시 → CI/CD 파이프라인 자동화 기반
- **alpine vs slim**: glibc/musl 차이로 ML 라이브러리 호환 문제 직접 찾아봄
- **-dit 옵션**: -d(백그라운드) + -i(interactive) + -t(tty) 조합

---

## Week 9 개선 예정

```
docker dive 적용:
→ 레이어별 크기 분석 → 불필요한 파일 제거

Multi-stage build:
→ builder stage + runtime stage
→ 현재 711MB → 목표 400MB 이하
```

---

## 오늘의 회고

### 배운 것

1. 레이어 순서 하나가 빌드 시간을 70배 바꿈 → 설계가 중요
2. Docker = 재현성 도구지만, 버전 고정 안 하면 의미 없음
3. FROM 선택도 이유가 있어야 함 (alpine ❌ slim ✅ 이유 설명 가능)

### 막혔던 부분

- numpy 버전 충돌 2번 → 직접 체험으로 해결
- glibc vs musl 개념 → 지금은 "alpine은 ML에서 안 쓴다" 정도 이해

### 내일 연결

- Day 6: FastAPI 기초 (오늘 만든 Docker 이미지 위에서 서빙!)

---

**Last Updated**: 2026.02.13 | **Status**: 완료 ✅
