# Day 28 트러블슈팅 - Airflow + MLflow 연동

> 날짜: 2026.03.24
> 작업: Airflow DAG에 MLflow 실험 추적 연동

---

## 트러블슈팅 테이블

| 에러                           | 원인                                                | 해결                                            |
| ------------------------------ | --------------------------------------------------- | ----------------------------------------------- |
| `Max retries exceeded`         | 로컬 MLflow를 Docker 안 Airflow가 접근 불가         | MLflow도 Docker Compose에 추가                  |
| `Invalid Host header 403`      | MLflow 3.x가 컨테이너 호스트명 차단                 | MLflow 2.13.0으로 다운그레이드 + IP로 직접 접근 |
| `webserver is already running` | 재시작 시 PID 파일이 볼륨에 남아있어 충돌           | `docker compose down -v`로 볼륨까지 삭제        |
| `Permission denied: '/mlflow'` | Airflow 컨테이너가 MLflow 컨테이너 폴더에 접근 불가 | `mlflow.log_artifact()` 제거                    |
| 포트 5001 충돌                 | 로컬 MLflow + Docker MLflow 둘 다 5001 사용         | 로컬 MLflow 종료 후 Docker MLflow만 실행        |

---

## 에러 상세

### 1. `Max retries exceeded` - 연결 실패

**에러 메시지**

```
HTTPConnectionPool(host='host.docker.internal', port=5001):
Max retries exceeded
```

**원인**

```
[Mac 로컬] mlflow ui --port 5001  ← 여기서 실행
[Docker]   Airflow               ← 여기서 실행

Airflow(Docker 안)에서 localhost = Docker 컨테이너 자신
Mac에서 localhost = 내 맥북
→ 서로 다른 localhost라서 접근 불가
```

**해결**

```yaml
# docker-compose.yml에 MLflow 서비스 추가
mlflow:
  build:
    context: .
    dockerfile: Dockerfile.mlflow
  container_name: mlflow_server
  ports:
    - "5001:5001"
  volumes:
    - mlflow-data:/mlflow
  command: >-
    mlflow server --host 0.0.0.0 --port 5001
    --backend-store-uri sqlite:////mlflow/mlflow.db
    --default-artifact-root /mlflow/artifacts
```

MLflow를 Docker 안으로 옮겨서 Airflow와 같은 네트워크에 배치.

---

### 2. `Invalid Host header 403` - 호스트 신뢰 안 함

**에러 메시지**

```
mlflow.exceptions.MlflowException: API request failed with error code 403
Response body: 'Invalid Host header - possible DNS rebinding attack detected'
```

**원인**

```
Airflow → "http://mlflow_server:5001 연결할게"
MLflow 3.x → "mlflow_server? 모르는 호스트명, 해킹 시도 차단" ❌
```

MLflow 3.x에서 보안이 강화되어 허용되지 않은 호스트명 차단.

**해결 시도 (실패)**

```yaml
# --host-allowlist 옵션 → MLflow 3.10.1에서 옵션명 다름
# --dev 옵션 → 동작 안 함
```

**최종 해결**

```dockerfile
# Dockerfile.mlflow - 버전 다운그레이드
FROM python:3.11-slim
RUN pip install --no-cache-dir mlflow==2.13.0
```

```python
# DAG 코드 - 호스트명 대신 IP로 직접 접근
MLFLOW_TRACKING_URI = "http://172.19.0.2:5001"
```

**주의**: Docker 재시작 시 IP가 바뀔 수 있음. 실무에서는 `--host-allowlist` 옵션이 정석.

---

### 3. `webserver is already running` - PID 충돌

**에러 메시지**

```
airflow.exceptions.AirflowException:
The webserver is already running under PID 21.
```

**원인**

```
Airflow 종료 시 → "나 PID 21번이야" 파일에 기록 (볼륨에 저장)
재시작 시 → "PID 21번 이미 실행 중" → 종료
(실제론 꺼진 상태인데 파일만 남아있음)
```

**해결**

```bash
docker compose down -v  # -v = 볼륨까지 완전 삭제
docker compose up -d
```

---

### 4. `Permission denied: '/mlflow'` - 파일 권한

**에러 메시지**

```
PermissionError: [Errno 13] Permission denied: '/mlflow'
```

**원인**

```
Airflow(컨테이너A) → MLflow(컨테이너B)의 /mlflow 폴더에 파일 저장 시도
컨테이너는 독립된 환경 → 다른 컨테이너 폴더 접근 불가
```

**해결**

```python
# evaluate_and_save 태스크에서 artifact 저장 제거
# mlflow.log_artifact(model_path) ← 이 줄 제거
# metric, param, tag만 기록
```

---

### 5. 포트 5001 충돌

**원인**

```
Mac 로컬: mlflow ui --port 5001 실행 중
Docker:   MLflow 컨테이너도 5001 사용
→ 같은 포트를 두 곳에서 사용하려 해서 충돌
```

**해결**

```bash
# 로컬 MLflow 종료 (Ctrl+C)
# Docker MLflow만 5001로 실행
```

---

## 핵심 교훈

```
1. Docker 컨테이너는 독립된 컴퓨터
   → localhost는 자기 자신만 가리킴
   → 다른 컨테이너 접근 = 서비스 이름 or IP 필요

2. 여러 서비스를 연동할 때는 같은 Docker Compose에 묶기
   → 같은 네트워크에 있어야 서로 통신 가능

3. docker compose down -v
   → 볼륨까지 삭제 (완전 초기화)
   → 단, DB/Variable 등 데이터도 날아감 주의

4. MLflow 버전별 보안 정책 다름
   → 2.x: 호스트 체크 없음
   → 3.x: 허용된 호스트만 접근 가능
```
