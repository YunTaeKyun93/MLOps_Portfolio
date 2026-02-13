# Day 5: Docker 기초

**날짜**: 2026.02.13
**강의**: [B] Part 1 - Ch 8 (도커 및 컨테이너 기술)

---

## 목표

> 오늘 만든 best_model.pkl을 Docker로 감싸는 것까지!
> 다음 주 FastAPI 서빙의 기반이 되는 날

| 항목        | 내용                                          |
| ----------- | --------------------------------------------- |
| 핵심        | Dockerfile 작성 → 이미지 빌드 → 컨테이너 실행 |
| 백엔드 관점 | Docker = "내 코드가 어디서든 똑같이 동작"     |
| 다음 연결   | Week 2 FastAPI 서빙 + Docker Compose          |

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

- [ ] 실습 1: Docker 설치 확인 + 기본 명령어
- [ ] 실습 2: Dockerfile 작성 + 이미지 빌드
- [ ] 실습 3: 이미지 최적화 (slim vs full 비교)
- [ ] 실습 4: .dockerignore 작성

### 정리

- [x] `notes/lecture_notes.md` 작성
- [ ] `notes/practice_notes.md` 작성

---

## 폴더 구조

```
day5-docker/
├── notes/
│   ├── lecture_notes.md
│   └── practice_notes.md
├── outputs/
│   └── best_model.pkl      # Day 4에서 복사
├── src/
│   └── predict.py          # Day 4에서 복사
├── .dockerignore
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 핵심 개념

### Docker 기본

- **Docker vs VM**: VM은 OS 전체 격리, Docker는 프로세스만 격리 → 가볍고 빠름
- **Image**: 패키징한 내용물 (붕어빵 틀) → 같은 Image로 Container 여러 개 실행 가능
- **Container**: 실행 중인 프로세스 (붕어빵)
- **Layer 캐시**: 자주 안 바뀌는 것 앞에 → 캐시 유지 → 빌드 속도 절약

### Dockerfile

- **FROM**: 베이스 이미지 (python:3.11-slim = ML 환경 표준)
- **WORKDIR**: 작업 디렉토리 설정
- **COPY 순서**: requirements.txt 먼저 → pip install → src/ 순서로 캐시 최적화
- **CMD**: 컨테이너 시작 시 실행할 명령어

### Docker Compose

- **왜 필요**: 여러 컨테이너 한번에 실행, 의존성 순서 보장, 환경변수 안전 관리
- **depends_on**: 서비스 실행 순서 보장 (DB 먼저 → 앱 실행)
- **volumes**: 컨테이너 꺼져도 데이터 유지 (영구 저장)

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

## 실습 결과 (실습 후 채우기)

### 이미지 크기 비교

| 베이스 이미지      | 크기 |
| ------------------ | ---- |
| python:3.11        |      |
| python:3.11-slim   |      |
| python:3.11-alpine |      |

### 빌드 시간 비교

| 상황                            | 시간 |
| ------------------------------- | ---- |
| 첫 빌드                         |      |
| 코드 수정 후 재빌드 (캐시 활용) |      |

---

## 트러블슈팅 (실습 중 채우기)

- ***

## 스스로 찾아보기 발견

- **docker dive**: 이미지 레이어별 크기 분석 도구 → Week 9 포트폴리오 최적화 때 활용 예정
- **docker tag**: Docker Hub에 이미지 게시 → CI/CD 파이프라인 자동화 기반
- **alpine vs slim**: glibc/musl 차이로 ML 라이브러리 호환 문제 직접 찾아봄

---

## Week 9 개선 예정

```
docker dive 적용:
→ 레이어별 크기 분석
→ 불필요한 파일 제거
→ 이미지 크기 XX% 절감 (실습 후 채우기)

Multi-stage build:
→ builder stage + runtime stage
→ 더 작은 최종 이미지
```

---

## 오늘의 회고

### 배운 것

1. 레이어 순서 하나가 빌드 속도를 완전히 바꿈 → 설계가 중요
2. FROM 선택도 이유가 있어야 함 (alpine ❌ slim ✅ 이유 설명 가능)
3. Docker Compose = 여러 컨테이너 의존성 + 환경변수 한번에 관리

### 막혔던 부분

- glibc vs musl 개념 → 지금은 "alpine은 ML에서 안 쓴다" 정도만 이해, 멀티스테이지 빌드 때 다시

### 내일 연결

- Day 5 실습: Dockerfile 직접 작성 + 이미지 빌드 + 크기 비교

---

**Last Updated**: 2026.02.13 | **Status**: 강의 완료 / 실습 진행 중 🔄
