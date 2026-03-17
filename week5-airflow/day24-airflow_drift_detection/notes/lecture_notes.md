# Day 24 강의 노트

**강의**: [P] Part4 Ch9-03~05 - 제조 이상 탐지 / 지속적인 모델 평가 및 재학습
**날짜**: 2026.03.16

---

## 오늘 들은 강의

✅ 09-03. Airflow 설치 (3:33)
✅ 09-04. Batch Train Inference 파이프라인 구축 (17:10)
✅ 09-05. Model Drift Trigger 기반 재학습 파이프라인 구축 (10:24)

---

## 핵심 아키텍처

```
Data
├── 최근 한달 데이터 → 월 단위 Batch → Train Pipeline
│                                           ↓
│                                         Model
│                                           ↓
└── 최근 일주일 데이터 → 주 단위 Batch → Inference Pipeline
                                            ↓
                                      Model Drift 감지
                                            ↓
                                         Trigger → Train Pipeline (재학습)
```

---

## 01. Batch Train / Inference 파이프라인

### 핵심 개념

- **Train Pipeline**: 월 단위로 최근 한달 데이터로 모델 재학습
- **Inference Pipeline**: 주 단위로 최근 일주일 데이터로 예측 실행
- **두 파이프라인이 분리된 이유**: 학습 주기 ≠ 예측 주기

### 백엔드 연결

```
Train Pipeline   = 월 1회 배치 작업 (cron job)
Inference Pipeline = 주 1회 예측 API 호출
Model            = DB에 저장된 최신 버전
```

---

## 02. Model Drift 감지

### Drift란?

모델이 학습할 때와 실제 운영 환경의 **데이터 분포가 달라지는 현상**

### Drift 종류

| 종류              | 의미                  |
| ----------------- | --------------------- |
| Data Drift        | 입력 데이터 분포 변화 |
| Concept Drift     | 정답 레이블 패턴 변화 |
| Performance Drift | 모델 성능 저하        |

### 감지 방법 (오늘 실습)

```python
threshold = baseline_rmse * 1.1  # 10% 이상 나빠지면 Drift
is_drift = current_rmse > threshold
```

### 백엔드 연결

```
Drift 감지    = 성능 모니터링 알람
Trigger       = 알람 → 자동 재학습 실행
threshold     = SLA 기준선
```

---

## 03. 자동 재학습 트리거

### 흐름

```
check_model_performance
        ↓
    detect_drift (임계값 비교)
    ├── Drift 있음 → retrain_model → notify
    └── Drift 없음 → skip
```

### 핵심 포인트

- Drift 없으면 재학습 안 함 → **불필요한 컴퓨팅 비용 절약**
- 임계값(threshold)을 얼마로 설정하냐가 핵심 결정사항
- 실제 서비스에서는 Slack/Email 알림 연동

---

## 해커톤 vs 실제 MLOps 비교

|               | 해커톤    | 실제 MLOps        |
| ------------- | --------- | ----------------- |
| 데이터        | 고정      | 계속 새로 들어옴  |
| 재학습 트리거 | 수동      | Drift 감지 → 자동 |
| MLflow 용도   | 실험 기록 | 모델 버전 관리    |
| Airflow 용도  | 불필요    | 자동화 핵심       |

---

## 💡 핵심 질문 5개

### Q1. Drift가 발생하는 원인은?

**A**: 실제 데이터 분포가 학습 데이터와 달라지기 때문. 예: 제조 공정 변경, 사용자 행동 변화, 계절성 등

### Q2. threshold를 너무 낮게 설정하면?

**A**: 사소한 성능 변화에도 재학습이 트리거되어 불필요한 컴퓨팅 비용 발생

### Q3. threshold를 너무 높게 설정하면?

**A**: 실제 성능이 많이 저하되었음에도 재학습이 안 되어 서비스 품질 저하

### Q4. Train/Inference 파이프라인을 왜 분리하나?

**A**: 학습은 비용이 크고 월 단위로 충분하지만, 예측은 최신 데이터 반영을 위해 더 자주 실행 필요

### Q5. 해커톤에서 Drift 감지가 의미없는 이유?

**A**: 해커톤은 데이터가 고정이라 분포 변화가 없음. Drift는 실제 서비스처럼 데이터가 계속 들어오는 환경에서 의미있음

---

## 💬 오늘 강의 한 줄 요약

> 모델은 한 번 만들고 끝이 아니라, 성능이 떨어지면 자동으로 감지하고 재학습하는 파이프라인이 실제 MLOps의 핵심이다.
