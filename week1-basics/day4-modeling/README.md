# Day 4: 모델 학습 & 평가

**날짜**: 2026.02.12
**강의**: [P] Part 2 - Chapter 1 (01-15 ~ 01-18)

---

## 목표

> 모델을 학습하고 `.pkl`로 저장하는 것까지!
> 저장한 모델은 다음 주 FastAPI 서빙에서 사용

| 항목        | 내용                               |
| ----------- | ---------------------------------- |
| 핵심        | 모델 학습 → 평가 → 저장            |
| 백엔드 관점 | 모델 파일 = 배포할 아티팩트        |
| 다음 연결   | Day 5 Docker → Week 2 FastAPI 서빙 |

---

## 진행 상황

### 강의

- [x] 01-15. Model Training (21분)
- [x] 01-16. Model Evaluation (29분)
- [x] 01-17. Model HyperParameter Tuning (12분)
- [x] 01-18. Model Selection (9분)

### 실습

- [x] 실습 0: joblib vs pickle 벤치마크 (`pickle_vs_joblib.py`)
- [x] 실습 1: 모델 학습 + `.pkl` 저장 (`train_model.py`)
- [x] 실습 2: 저장된 모델 로드 + 예측 (`predict.py`)
- [x] 실습 3: 3개 모델 비교 + 최고 모델 저장 (`compare_models.py`)

### 정리

- [x] `notes/lecture_notes.md` 작성
- [x] `notes/practice_notes.md` 작성

---

## 폴더 구조

```
day4-modeling/
├── data/
│   └── titanic/
│       └── train.csv
├── notes/
│   ├── lecture_notes.md     # 강의 정리
│   └── practice_notes.md    # 실습 배운 것
├── outputs/
│   ├── titanic_model.pkl    # 학습된 모델
│   └── best_model.pkl       # 최고 성능 모델
├── src/
│   ├── pickle_vs_joblib.py  # 실습 0 (벤치마크)
│   ├── train_model.py       # 실습 1
│   ├── predict.py           # 실습 2
│   └── compare_models.py    # 실습 3
└── README.md
```

---

## 핵심 개념

### Model Training

- **Overfitting**: 학습 데이터에만 너무 맞춰져서 실제 데이터에서 성능 떨어짐
- **Train/Test Split**: 학습용 80% / 평가용 20% 분리
- **random_state**: 재현성을 위한 seed 고정 → config에서 통일 관리

### Model Evaluation

- **Accuracy vs F1-Score**: 불균형 데이터에서 Accuracy는 함정, F1-Score 사용
- **Precision**: 내가 맞다고 한 것 중 진짜 맞은 비율 (FP 비용 클 때)
- **Recall**: 전체 정답 중 맞춘 비율 (FN 비용 클 때 → 사기 탐지, 암 진단)
- **평가 지표 선택**: 비즈니스 목적에 따라 달라짐

### HyperParameter Tuning

- **Parameter**: 모델이 학습하면서 자동으로 찾는 값 (가중치)
- **HyperParameter**: 사람이 학습 전에 설정하는 값 (n_estimators, max_depth)
- **Tuning 방법**: Grid Search (전체 탐색) → Random Search (빠름) → Bayesian (효율적)

### Model Selection

- 성능(F1) + 속도(서빙) + 해석 가능성 + 데이터 크기 + 유지보수 종합 고려

---

## 백엔드 연결

```
train_test_split  = 개발 DB / 테스트 DB 분리
random_state=42   = 테스트 환경 고정 (재현성)
joblib.dump()     = 빌드 아티팩트 저장
model.pkl         = 배포할 파일
joblib.load()     = 서버 시작 시 모델 로드
predict()         = API response 반환
compress=0        = Redis 캐시 (속도 우선)
compress=3        = S3 장기 보관 (압축)
```

---

## 실습 결과

### joblib compress 벤치마크

| compress | save   | load   | size   |
| -------- | ------ | ------ | ------ |
| 0        | 0.028s | 0.019s | 76.3MB |
| 3        | 3.193s | 0.512s | 68.9MB |
| 9        | 3.548s | 0.474s | 68.5MB |

→ 서빙 환경: compress=0 / 스토리지 절약: compress=3

### 모델 성능 비교

| 모델                | Accuracy   | F1-Score   |
| ------------------- | ---------- | ---------- |
| Logistic Regression | 0.7933     | 0.7132     |
| Decision Tree       | 0.8045     | 0.7407     |
| **Random Forest**   | **0.8268** | **0.7597** |

### 최고 성능 모델

- **모델명**: Random Forest
- **F1-Score**: 0.7597
- **저장 경로**: `outputs/best_model.pkl`

---

## 트러블슈팅

### Feature Mismatch 에러

**상황**: predict.py 실행 시 에러 발생

```
Feature names seen at fit time, yet now missing:
- Embarked_C
- Sex_female
```

**원인**: 학습(11개 컬럼) vs 예측 입력(8개 컬럼) 불일치

**해결**:

```python
expected_cols = model.feature_names_in_
for col in expected_cols:
    if col not in new_passenger.columns:
        new_passenger[col] = 0
new_passenger = new_passenger[expected_cols]
```

**배운 것**: Day 3 get_dummies vs OneHotEncoder 직접 체감
→ 프로덕션에서 OneHotEncoder 써야 하는 이유!

---

## Week 9 개선 예정 🔥

```
현재 F1: 0.7597

개선 계획:
- Name에서 호칭(Mr/Mrs/Master) 추출
- 호칭별 Age 결측치 처리
- SibSp + Parch → FamilySize 파생 변수

예상 F1: 0.82~0.85
스토리: "도메인 지식으로 성능 개선"
```

---

## 오늘의 회고

### 배운 것

1. joblib compress 트레이드오프 (속도 vs 용량)
2. Feature Mismatch 에러 직접 체험 → OneHotEncoder 필요성 체감
3. 평가 지표는 비즈니스 목적에 따라 달라짐

### 막혔던 부분

- Feature Mismatch 에러 → model.feature*names_in*으로 해결

### 내일 연결

- Day 5: Docker로 오늘 만든 모델 컨테이너화 🐳

---

**Last Updated**: 2026.02.12 | **Status**: 완료 ✅
