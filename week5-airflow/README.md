# MLOps ML 파이프라인 - 영화 추천 모델 자동화

영화 추천 SVD 모델의 자동 재학습부터 실험 추적, 성능 모니터링까지 E2E MLOps 파이프라인 구현.

---

## 아키텍처

```
[MovieLens 데이터]
        ↓
[Airflow ETL DAG]        매일 자동 실행
  extract → transform → load (SQLite)
        ↓
[Airflow 재학습 DAG]     매일 자동 실행
  load_data → preprocess → train_model → evaluate_and_save
        ↓                       ↓
[best_model.pkl 저장]   [MLflow 실험 추적]
                          - RMSE, n_factors, n_epochs 기록
                          - Model Registry 등록 (Staging)
        ↓
[Airflow Drift 감지 DAG] 매일 자동 실행
  check_performance → detect_drift → retrain → notify
                                                  ↓
                                          [Slack 알림]
        ↓
[FastAPI 추천 API]
  GET /recommend/{user_id}
  POST /predict
        ↓
[Prometheus] → 15초마다 /metrics 수집
        ↓
[Grafana] → API 요청 수, 응답시간 시각화
```

---

## 기술 스택

| 분류       | 기술                   |
| ---------- | ---------------------- |
| ML         | scikit-surprise (SVD)  |
| 워크플로우 | Apache Airflow 2.7.3   |
| 실험 추적  | MLflow 2.13.0          |
| API 서빙   | FastAPI, Uvicorn       |
| 모니터링   | Prometheus, Grafana    |
| 알림       | Slack Incoming Webhook |
| 컨테이너   | Docker, Docker Compose |

---

## DAG 구성

### 1. movielens_etl (매일 실행)

```
extract → transform → load

- CSV 데이터 로드 (없으면 샘플 데이터 자동 생성)
- 결측치 제거, 타입 캐스팅, 중복 제거
- SQLite DB에 저장
```

### 2. movie_retrain (매일 실행)

```
load_data → preprocess → train_model → evaluate_and_save

- SVD 모델 학습 (n_factors=50, n_epochs=20)
- 이전 모델보다 RMSE 낮을 때만 저장
- MLflow에 실험 자동 기록
- 성능 개선 시 Model Registry에 자동 등록 (Staging)
```

### 3. drift_detection_dag (매일 실행)

```
check_model_performance → detect_drift → retrain_model → notify

- baseline_rmse × 1.1 초과 시 Drift 판정
- Drift 감지 시 자동 재학습 트리거
- Slack으로 결과 알림
```

---

## MLflow 실험 추적

```
Experiment: movie-recommend-svd
  └── Run: svd-20260324-0537
        ├── Parameters
        │     ├── n_factors: 50
        │     ├── n_epochs: 20
        │     ├── test_size: 0.2
        │     └── data_size: 100
        ├── Metrics
        │     └── rmse: 0.71
        └── Tags
              ├── model_type: SVD
              ├── data_source: movielens
              └── triggered_by: airflow

Model Registry: svd-movie-recommend
  └── Version 1 (Stage: Staging)
```

---

## 모니터링

### Prometheus

- FastAPI `/metrics` 엔드포인트 15초마다 수집
- 수집 메트릭: 요청 수, 응답시간, 에러율

### Grafana 대시보드

- API 초당 요청 수 (`rate(http_requests_total[1m])`)
- 엔드포인트별 요청 분포

---

## 실행 방법

```bash
# 1. 전체 서비스 실행
cd week5-airflow/day21-airflow-basic/airflow_practice
docker compose up -d

# 2. 서비스 접속
Airflow:    http://localhost:8080  (admin/admin)
MLflow:     http://localhost:5001
Prometheus: http://localhost:9090
Grafana:    http://localhost:3000  (admin/admin)
FastAPI:    http://localhost:8001
```

---

## 트러블슈팅

| 문제                           | 원인                                     | 해결                           |
| ------------------------------ | ---------------------------------------- | ------------------------------ |
| Airflow → MLflow 연결 실패     | 컨테이너 간 localhost 불통               | MLflow를 Docker Compose에 추가 |
| MLflow 3.x Host 헤더 차단      | 보안 강화로 컨테이너 호스트명 차단       | MLflow 2.13.0으로 다운그레이드 |
| artifact 저장 권한 에러        | Airflow/MLflow 다른 컨테이너라 접근 불가 | mlflow-data 볼륨 공유          |
| Airflow webserver PID 충돌     | 강제 종료 시 PID 파일 잔존               | 시작 시 PID 파일 자동 삭제     |
| Prometheus → FastAPI 연결 실패 | 포트 혼동 (외부/내부)                    | 내부 포트(8000)로 접근         |

---

## 폴더 구조

```
week5-airflow/
├── day21-airflow-basic/
│   └── airflow_practice/
│       ├── Dockerfile              ← Airflow 이미지
│       ├── Dockerfile.mlflow       ← MLflow 2.13.0 이미지
│       ├── docker-compose.yml      ← 전체 서비스 구성
│       ├── docker-data/
│       │   ├── prometheus/config/prometheus.yml
│       │   └── grafana/data/
│       └── dags/
│           ├── movielens_etl_dag.py
│           ├── movie_retrain_dag.py
│           ├── drift_detection_dag.py
│           └── my_dag.py
├── day28-mlflow-airflow/
│   └── troubleshooting.md
└── week5-airflow-pipeline.md
```

---

## 개선 예정

- [ ] Prometheus Alert 설정 (RMSE 임계값 초과 시 알림)
- [ ] MLflow IP 하드코딩 → 서비스 이름으로 변경 (3.x 보안 이슈 해결)
- [ ] 실제 MovieLens 1M 데이터 연동 (현재 샘플 데이터)
- [ ] Model Registry Production 승격 자동화
