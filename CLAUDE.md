# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

12주 MLOps 포트폴리오 프로젝트. NestJS 백엔드 경험을 바탕으로 ML 서빙/배포 역량을 갖춘 백엔드 개발자 성장 기록. 목표 포지션: **백엔드 개발자 + ML 서빙 경험**.

## Repository Structure

```
week1-basics/          # ML 기초 (PyTorch, scikit-learn, Docker, BentoML)
week2-serving/         # FastAPI 서빙, CF 추천 시스템
week3-kubernetes-cicd/ # Kubernetes 배포, CI/CD
week4-aws/             # AWS ECS, S3, minikube
week5-airflow/         # Airflow DAG, MLflow, Prometheus, Grafana
week7-django/          # Django + DRF 기초 실습
project1-movie-recommend/  # 포트폴리오 #1 (메인 프로젝트)
```

## Commands by Project

### project1-movie-recommend (FastAPI + CF)

```bash
# 모델 학습
cd project1-movie-recommend
python src/train.py

# 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000

# 테스트 (9개 테스트 케이스)
pytest test_service.py -v

# Docker 빌드 (M1 Mac → ECS 배포 시 반드시 linux/amd64 지정)
docker build --platform linux/amd64 -t movie-recommend .
docker run -p 8000:8000 movie-recommend

# docker-compose
docker compose up -d
```

### week5-airflow (Airflow + MLflow + Prometheus + Grafana)

```bash
cd week5-airflow/day21-airflow-basic/airflow_practice
docker compose up -d

# 서비스 접속
# Airflow:    http://localhost:8080  (admin/admin)
# MLflow:     http://localhost:5001
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000  (admin/admin)
# FastAPI:    http://localhost:8001
```

### week7-django (Django + DRF)

```bash
cd week7-django

# uv로 패키지 관리 (pyproject.toml + uv.lock)
uv sync

# DB 마이그레이션 및 서버 실행
python manage.py migrate
python manage.py runserver

# 단일 앱 마이그레이션 생성
python manage.py makemigrations movies
python manage.py makemigrations directors
```

## Architecture

### project1-movie-recommend

NestJS 레이어드 아키텍처를 FastAPI로 옮긴 구조:

| 파일 | NestJS 대응 | 역할 |
|------|------------|------|
| `app/routers/recommend.py` | Controller | API 엔드포인트 |
| `app/services/recommend.py` | Service | 모델 로드/추론 비즈니스 로직 |
| `app/schemas/recommend.py` | DTO | Request/Response Pydantic 모델 |
| `main.py` | AppModule | FastAPI 앱 + `lifespan` (서버 시작 시 모델 로드) |
| `src/train.py` | — | User-Based CF 모델 학습, `outputs/*.pkl` 저장 |

모델 저장 기준: `outputs/best_acc.txt`에 기록된 RMSE보다 낮을 때만 갱신.

### week5-airflow DAG 구성

3개의 독립 DAG (모두 매일 실행):
- `movielens_etl`: CSV → 전처리 → SQLite
- `movie_retrain`: SVD 학습 → RMSE 비교 → MLflow 실험 추적 → Model Registry(Staging)
- `drift_detection_dag`: baseline RMSE × 1.1 초과 시 재학습 트리거 + Slack 알림

### week7-django

DRF `DefaultRouter`로 ViewSet 자동 라우팅. `config/urls.py`에서 `movies`, `directors` ViewSet을 `api/` prefix로 등록.

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`):
- `check` job: 항상 통과 (Branch Protection Required status check)
- `test` job: `project1-movie-recommend` 경로 변경 시에만 실행
  - pytest → Docker build (linux/amd64) → AWS ECR push → K8s rolling update

ECR: `947632012584.dkr.ecr.ap-northeast-2.amazonaws.com/movie-recommend`
필요 시크릿: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `KUBE_CONFIG`

## 브랜치 전략

- 네이밍: `feat/day{N}-{작업}` / `docs/day{N}-{내용}` / `chore/{내용}`
- 예시: `feat/day8-predict-bugfix`, `docs/day8-notes`
- main 직접 push 금지
- 작업 전 반드시 새 브랜치 생성

## 커밋 규칙

- 커밋 전 pytest 실행 확인
- 컨벤션: `feat(scope): 설명` / `refactor: 설명` / `fix: 설명`
- 한국어 설명 사용

## Key Notes

- **M1 Mac**: Docker 빌드 시 반드시 `--platform linux/amd64` 지정 (ECS/K8s는 amd64)
- **MLflow 버전**: 3.x는 컨테이너 호스트명 보안 이슈로 2.13.0 사용
- **평가 지표**: 평점 예측은 회귀 문제 → Accuracy 대신 RMSE 사용
- **콜드 스타트**: 미지원 user_id/movie_id → 기본값 3.0 반환
- **Python 환경**: conda mlops-study (3.11.14)
- **pytest 실행**: `conda run -n mlops-study python -m pytest`
