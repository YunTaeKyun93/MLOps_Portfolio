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

- [ ] 01-15. Model Training (21분)
- [ ] 01-16. Model Evaluation (29분)
- [ ] 01-17. Model HyperParameter Tuning (12분)
- [ ] 01-18. Model Selection (9분)

### 실습

- [ ] 실습 1: 모델 학습 + `.pkl` 저장 (`train_model.py`)
- [ ] 실습 2: 저장된 모델 로드 + 예측 (`predict.py`)
- [ ] 실습 3: 3개 모델 비교 + 최고 모델 저장 (`compare_models.py`)

### 정리

- [ ] `notes/lecture_notes.md` 작성
- [ ] `notes/practice_notes.md` 작성

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
│   ├── train_model.py       # 실습 1
│   ├── predict.py           # 실습 2
│   └── compare_models.py    # 실습 3
└── README.md
```

---

## 핵심 개념 (강의 후 채우기)

### Model Training

- Overfitting:
- Train/Test Split:
- random_state:

### Model Evaluation

- Accuracy vs F1-Score:
- Precision / Recall:
- 언제 어떤 지표를 쓰나:

### HyperParameter Tuning

- HyperParameter vs Parameter:
- Tuning 방법:

### Model Selection

- 선택 기준:

---

## 백엔드 연결

```
train_test_split  = 개발 DB / 테스트 DB 분리
random_state=42   = 테스트 환경 고정 (재현성)
joblib.dump()     = 빌드 아티팩트 저장
model.pkl         = 배포할 파일
joblib.load()     = 서버 시작 시 모델 로드
predict()         = API response 반환
```

---

## 실습 결과 (실습 후 채우기)

### 모델 성능 비교

| 모델                | Accuracy | F1-Score |
| ------------------- | -------- | -------- |
| Logistic Regression |          |          |
| Decision Tree       |          |          |
| Random Forest       |          |          |

### 최고 성능 모델

- 모델명:
- F1-Score:
- 저장 경로: `outputs/best_model.pkl`

---

## 오늘의 회고 (하루 끝나고 채우기)

### 배운 것

1.
2.
3.

### 막혔던 부분

-

### 내일 연결

- Day 5: Docker로 오늘 만든 모델 컨테이너화

---

**Last Updated**: 2026.02.12 | **Status**: 진행 중 🔄

🔍 스스로 찾아보기 (약 1시간)

검색 또는 GPT 활용 → practice_notes.md에 기록
포트폴리오 "기술 선택 이유" 재료 수집!

[VS] joblib vs pickle
찾아볼 것:

- 둘 다 모델 저장인데 왜 ML에서 joblib을 쓰나?
- 속도 차이가 있나?
- numpy array 포함된 객체에서 차이는?

→ 나중에 README에:
"모델 저장 시 joblib을 선택한 이유"로 활용!
[WHAT IF] random_state 없애면?
직접 실험:

1. train_model.py에서 random_state=42 제거
2. 3번 실행해서 accuracy 비교
3. 결과가 매번 다른지 확인

→ 재현성이 왜 중요한지 체감!
→ 백엔드 연결: 테스트 환경 고정과 동일
[WHY] F1-Score를 Accuracy보다 중요하게 보는 이유
찾아볼 것:

- Accuracy 90%인데 왜 나쁜 모델일 수 있나?
- Precision vs Recall 트레이드오프
- 실무에서 어떤 상황에 어떤 지표를 쓰나?

힌트: Day 3 Class Imbalance와 연결됨!
→ "95:5 불균형 데이터에서 Accuracy=95%의 함정"

📝 오늘 practice_notes.md 추가할 것
markdown## 실습 4: 모델 학습 & 평가

### [VS] joblib vs pickle

- 발견한 차이:
- ML에서 joblib 쓰는 이유:
- 포트폴리오 활용:

### [WHAT IF] random_state 실험

- random_state 있을 때 accuracy:
- random_state 없을 때 (3회 실행):
  - 1회:
  - 2회:
  - 3회:
- 결론:

### [WHY] F1-Score vs Accuracy

- Accuracy의 함정:
- 실무 선택 기준:
- Day 3 Class Imbalance와 연결:
