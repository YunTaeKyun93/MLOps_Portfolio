# Day 25 실습 노트

**날짜**: 2026.03.16
**목표**: Drift 감지 + 자동 재학습 트리거 DAG 구현

---

## 실습: drift_detection_dag.py

### 목표

- [x] Drift 감지 로직 구현
- [x] 임계값 기반 자동 재학습 트리거
- [x] XCom으로 태스크 간 데이터 전달 확인
- [x] Airflow UI에서 실행 결과 확인

### DAG 구조

```
check_model_performance
        ↓
    detect_drift
    ├── True  → retrain_model → notify
    └── False → retrain_model(skip) → notify
```

### 핵심 코드

```python
@task
def detect_drift(metrics: dict):
    current = metrics["current_rmse"]
    baseline = metrics["baseline_rmse"]
    threshold = baseline * 1.1  # 10% 이상 나빠지면 Drift

    is_drift = current > threshold
    return is_drift

@task
def retrain_model(is_drift: bool):
    if is_drift:
        print("Drift 감지됨 → 모델 재학습 시작")
        return new_rmse
    else:
        print("Drift 없음 → 재학습 스킵")
        return None
```

### XCom 실행 결과

| Task                    | Return Value                                      | 의미                        |
| ----------------------- | ------------------------------------------------- | --------------------------- |
| check_model_performance | `{'current_rmse': 0.97, 'baseline_rmse': 0.956}`  | 성능 측정                   |
| detect_drift            | `False`                                           | 0.97 < 1.0516 → Drift 아님  |
| check_model_performance | `{'current_rmse': 1.127, 'baseline_rmse': 0.956}` | 성능 측정                   |
| detect_drift            | `True`                                            | 1.127 > 1.0516 → Drift 감지 |
| retrain_model           | `0.925`                                           | 재학습 후 새 RMSE           |

### threshold 계산

```
baseline_rmse = 0.956
threshold = 0.956 * 1.1 = 1.0516

0.97  < 1.0516 → Drift 아님 (재학습 스킵)
1.127 > 1.0516 → Drift 감지 (재학습 실행)
```

---

## 🔥 트러블슈팅

없음

---

## ✅ 오늘 완성한 것

- [x] `dags/drift_detection_dag.py`: Drift 감지 + 자동 재학습 DAG

---

## 📝 회고

- **배운 것**: Drift 감지는 threshold 설정이 핵심. 너무 낮으면 불필요한 재학습, 너무 높으면 성능 저하 방치
- **연결**: 해커톤(MLflow 실험 기록) vs 실제 서비스(Airflow Drift 자동화) 차이 명확히 이해
- **내일 연결**: Week 5 마무리 → 데이터 파이프라인 문서화

---

## Git 커밋

```bash
git add dags/drift_detection_dag.py
git commit -m "feat/day25: Drift 감지 + 자동 재학습 트리거 DAG 구현"
git push
```
