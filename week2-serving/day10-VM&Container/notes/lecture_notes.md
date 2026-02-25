# Day 10 강의 노트 - 환경 관리 툴 + Container 이론

**강의**: [P] Part2 Ch3-03~06
**날짜**: 2026.02.19

---

## Part 1. 환경 관리 툴 (Ch3-03~04)

### 핵심 개념

- 환경 격리: 프로젝트별 Python 버전/패키지 독립
- 재현성: environment.yml / Pipfile.lock으로 동일 환경 재현
- Python 레벨 격리(Conda) vs OS 레벨 격리(Docker)

### 도구 비교

| 도구       | 특징                     | 언제                 |
| ---------- | ------------------------ | -------------------- |
| Conda      | Python+R, 크로스플랫폼   | ML 로컬 개발         |
| Virtualenv | Python only, 가벼움      | 단순 Python 프로젝트 |
| Pipenv     | pip+venv 통합, lock 파일 | 협업 Python 프로젝트 |
| Docker     | OS째 격리                | 서비스 배포          |

### 핵심 커맨드

```bash
# Conda
conda create --name myenv python=3.8
conda activate myenv
conda env export > environment.yml
conda env create -f environment.yml

# Virtualenv
virtualenv myenv && source myenv/bin/activate
```

### 백엔드 연결

- environment.yml = package.json (의존성 명세)
- Pipfile.lock = package-lock.json (버전 고정)
- Docker = 서버째 패키징 (npm보다 상위 개념)

### 계층 구조

```
Application → Python Env(Conda) → OS → Docker → Host OS
```

### 핵심 질문 5개

1. Conda와 Docker를 동시에 쓰는 이유는?
   - 로컬 실험은 conda로 빠르게, 확정된 패키지를 Docker에 박아넣는 워크플로우
2. environment.yml과 requirements.txt 차이는?
   - environment.yml = conda용 / requirements.txt = pip용 (Docker 안에서 주로 사용)
3. Pipfile.lock이 중요한 이유는?
   - package-lock.json처럼 정확한 버전 고정 → 6개월 후에도 동일 환경 재현
4. 실무에서 로컬 개발 → 배포 환경 전환 프로세스는?
   - conda로 개발 → pip freeze > requirements.txt → Dockerfile에서 pip install
5. Docker 없이 Conda만으로 배포하면 안 되는 이유는?
   - OS가 다르면 ImportError 등 환경 불일치 발생

### 한 줄 요약

> 로컬 실험은 Conda, 배포는 Docker - 둘은 대체재가 아니라 상호보완

---

## Part 2. Container 이론 + 실습 (Ch3-05~06)

### Container란?

애플리케이션 + 코드 + 런타임 + 시스템 라이브러리를 포함한 표준화된 실행 단위

- OS 커널은 공유
- 파일 시스템은 격리
- 실행 환경을 통째로 묶음

### VM vs Container

| 항목      | VM                 | Container       |
| --------- | ------------------ | --------------- |
| OS        | 각 VM마다 Guest OS | 커널 공유       |
| 무게      | 무거움             | 가벼움          |
| 속도      | 느림               | 빠름            |
| 격리 수준 | 강함               | 상대적으로 약함 |

### 핵심 구성요소

- **Image**: 실행 환경 설계도 (불변, Dockerfile로 생성)
- **Registry**: 이미지 저장소 (Docker Hub, ECR, GCR)
- **Runtime**: 이미지 실행 엔진 (Docker, containerd)

### Docker 구성요소

- Docker Image
- Docker Container
- Docker Daemon
- Docker Registry
- Docker Client

### 백엔드 연결

| Container     | 백엔드 비유                  |
| ------------- | ---------------------------- |
| Dockerfile    | package.json + 빌드 스크립트 |
| Image         | 빌드 결과물 (dist/)          |
| Registry      | npm registry                 |
| Container     | 실행 중인 Node 프로세스      |
| Docker Daemon | pm2 같은 프로세스 매니저     |

### 왜 MLOps에서 필수?

torch + CUDA + numpy + glibc 버전 조합이 딱 맞아야 모델이 돌아감
→ Container 없으면 환경 불일치로 반드시 사고남

### Container 장단점

**장점**: 빠른 시작, 환경 일관성, 자원 효율성, 격리  
**단점**: VM보다 격리 약함, 여러 컨테이너 관리 복잡 → **그래서 Kubernetes 등장**

### 오늘 실습 결과

- Docker Hub 배포: `yuntaekyun/sklearn_model` ✅
- Health check Dockerfile 최적화 ✅
- 트러블슈팅: `loacalhost` 오타 → `localhost` 수정 ✅

### 최종 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY outputs/*.pkl ./outputs/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.service:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 핵심 질문 5개

1. Container가 VM보다 가벼운 이유는?
   OS 커널을 Host OS와 공유하기 때문. VM은 Guest OS 전체(수 GB)를 올리지만 Container는 앱 실행에 필요한 것만 패키징. 그래서 MB 단위로 가능
2. Image가 immutable(불변)인 이유는?
   빌드 시점에 확정된 스냅샷이라서. 실행 중에 내부를 바꿔도 컨테이너 재시작하면 원래대로 돌아옴. 새 버전 필요하면 새로 빌드해야 해. 이게 재현성의 핵심 - 어디서 실행해도 동일한 결과 보장.
3. Docker Hub 말고 다른 Registry는?
   - AWS → ECR (Elastic Container Registry)
   - GCP → GCR / Artifact Registry
   - 사내 온프레미스 → Harbor
   - GitHub → GitHub Container Registry (ghcr.io)
4. Container 여러 개 관리가 어려운 이유는?
   docker-compose는 로컬 멀티컨테이너용이고, 실제 운영에서는:

- 컨테이너 100개를 어떤 서버에 올릴지 -죽으면 자동 재시작 -트래픽 분산
- 롤링 업데이트

5. ML 모델 서빙에 Container가 필수인 이유는?

torch + CUDA + numpy + glibc 버전 조합이 딱 맞아야 모델이 돌아감. 이 조합이 서버마다 다르면 100% 사고남. Container로 환경째로 박제하면 로컬이든 서버든 동일하게 실행 보장.

### 한 줄 요약

> Container = 환경째로 박제. ML에서 선택 아닌 필수.
