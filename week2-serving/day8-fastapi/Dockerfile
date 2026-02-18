# ─────────────────────────────────────────────
# Stage 1: Base Image
# ─────────────────────────────────────────────
FROM python:3.11-slim
# python:3.11-slim = 경량화된 Python 이미지
# slim = 불필요한 패키지 제거된 버전 (용량 작음)
# 백엔드 관점: node:18-alpine 같은 개념

# 작업 디렉토리 설정
WORKDIR /app
# 컨테이너 내부에서 /app 폴더가 기본 경로
# 이후 모든 명령어는 /app 기준으로 실행됨

# 시스템 패키지 업데이트 (보안)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
# apt-get update         = 패키지 목록 업데이트
# --no-install-recommends = 추천 패키지 설치 안 함 (용량 절약)
# rm -rf /var/lib/apt/lists/* = 캐시 삭제 (레이어 크기 줄이기)

# ─────────────────────────────────────────────
# Stage 2: Dependencies
# ─────────────────────────────────────────────
# requirements.txt 먼저 복사 (레이어 캐싱 최적화)
# 코드 변경되어도 패키지는 다시 설치 안 해도 됨
COPY requirements.txt .
# 로컬의 requirements.txt를 컨테이너 /app/requirements.txt로 복사

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt
# --no-cache-dir = pip 캐시 저장 안 함 (이미지 용량 절약)
# 백엔드 관점: npm install --production 같은 개념

# ─────────────────────────────────────────────
# Stage 3: Application Code
# ─────────────────────────────────────────────
# 소스 코드 복사
COPY src/ ./src/
# 로컬 src/ 폴더를 컨테이너 /app/src/로 복사

# ─────────────────────────────────────────────
# Stage 4: Model Files
# Day 7에서 학습한 pkl 파일 복사
# ─────────────────────────────────────────────
# day8-fastapi/outputs 폴더에 이미 복사해둠
COPY outputs/*.pkl ./outputs/
# 로컬 outputs/*.pkl을 컨테이너 /app/outputs/로 복사

# ─────────────────────────────────────────────
# Stage 5: Run
# ─────────────────────────────────────────────
# 포트 노출
EXPOSE 8000
# 컨테이너가 8000 포트를 사용한다고 선언 (문서화 목적)
# 실제 포트 매핑은 docker run -p 8000:8000 에서 함

# 서버 실행
# --host 0.0.0.0 : 외부 접근 허용 (중요!)
# --port 8000    : 컨테이너 내부 포트
CMD ["uvicorn", "src.service:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD = 컨테이너 실행 시 기본 명령어
# 0.0.0.0 = 모든 IP에서 접근 허용 (localhost만 쓰면 외부 접근 안 됨!)