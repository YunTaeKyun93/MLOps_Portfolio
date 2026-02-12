# Day 4 실습 노트

**날짜**: 2026.02.12
**실습**: 모델 학습, 저장, 비교

---

## 실습 0: joblib vs pickle 벤치마크

### [VS] pickle vs joblib 기본 비교

**둘 다 처음 들어봐서 먼저 뭔지부터 찾아봄:**

```
파이썬 객체를 파일로 저장했다가 나중에 다시 불러오는 도구
모델은 RAM에만 존재 → 껐다 켜지면 사라짐
→ 파일로 저장해서 나중에 재사용
```

| 항목         | pickle    | joblib        |
| ------------ | --------- | ------------- |
| 기본 제공    | O         | X (설치 필요) |
| 범용성       | 매우 넓음 | ML 중심       |
| 대용량 numpy | 보통      | 더 효율적     |
| ML 관행      | 사용 가능 | 더 많이 사용  |

**벤치마크 결과 (numpy 배열 40MB):**

```
[pickle] save: 0.009s | load: 0.006s | size: 38.1MB
[joblib] save: 0.013s | load: 0.011s | size: 38.1MB
```

**발견한 것:**

- 단순 numpy 배열 하나는 차이 없음
- joblib 강점은 numpy 배열 여러 개 섞인 복잡한 객체
- sklearn 모델 저장할 때 진짜 차이남

**결론:**

- 단순 객체 → pickle OK
- sklearn 모델 → joblib 선택
- ML 관행상 joblib이 표준

---

### [VS] joblib compress 옵션 실험

**실험 결과:**

| compress | save   | load   | size   |
| -------- | ------ | ------ | ------ |
| 0        | 0.028s | 0.019s | 76.3MB |
| 3        | 3.193s | 0.512s | 68.9MB |
| 9        | 3.548s | 0.474s | 68.5MB |

**발견한 것:**

- compress=0 vs 3: 저장 100배, 로드 20배 차이
- compress=3 vs 9: 용량 차이 0.4MB (거의 없음)
- 속도 vs 용량 트레이드오프 존재

**언제 뭘 쓰나:**

```
compress=0 → 서빙 환경 (로드 속도 우선)
compress=3 → 스토리지 절약 필요할 때 (S3 업로드)
compress=9 → 거의 안 씀 (3 대비 이득 없음)
```

**백엔드 비유:**

```
compress=0 = Redis 캐시 (빠르지만 공간 차지)
compress=3 = S3 장기 보관 (압축해서 저장)
```

**포트폴리오 활용:**

```
"FastAPI 서빙 환경에서 compress=0 선택
 이유: 로드 속도가 API 응답 시간에 직결
 스토리지 절약보다 응답 속도 우선"
```

---

## 실습 1: 모델 학습 + 저장 (train_model.py)

### 결과

```
Train: 712개 / Test: 179개
Accuracy: 0.8268

              precision  recall  f1-score
Not Survived    0.83      0.90      0.86
Survived        0.82      0.71      0.76
```

### 배운 것

#### target_names 안전하게 쓰기

**발견한 문제:**

```python
# ⚠️ 위험: 클래스 순서에 의존
target_names=['Not Survived', 'Survived']

# ✅ 안전: 명시적 매핑
labels=[0, 1],
target_names=['Not Survived', 'Survived']
```

**왜?:**

- y에 클래스가 등장하는 순서에 따라 매핑이 달라질 수 있음
- labels 명시 → 0은 항상 Not Survived, 1은 항상 Survived

**백엔드 비유:**

```
Enum 값 순서에 의존하지 말고
명시적으로 매핑하는 것과 동일
```

#### 결과 해석 - 어떤 지표가 중요한가?

타이타닉처럼 이미 사고가 난뒤 의 결과보고면 뭘 중요하게 봐야할까?
사망처리가 되었는데 살아있는 사람?
살아있는데 죽었다고 판정된사람?

**타이타닉 사후 분석이라면:**

```
→ F1-Score (균형)
  특별히 Recall/Precision 한쪽을
  중요하게 볼 비즈니스 목적 없음
```

**만약 실제 서비스였다면:**

```
구조대 파견 목적:
→ Recall 중요 (생존자 1명도 놓치면 안 됨)
   현재 생존자 Recall = 0.71
   → 실제 생존자 29% 사망으로 예측 (심각!)

보험금 지급 목적:
→ Precision 중요 (오지급 방지)
```

**핵심 깨달음:**

```
같은 모델도 비즈니스 목적에 따라
평가 기준이 달라진다!
```

---

## 실습 2: 모델 로드 + 예측 (predict.py)

### 트러블슈팅: Feature Mismatch 에러

**에러:**

```
Feature names seen at fit time, yet now missing:
- Embarked_C
- Sex_female
```

**원인:**

```
학습 컬럼 (11개): Sex_female, Sex_male,
                  Embarked_C, Embarked_Q, Embarked_S
예측 입력 (8개):  Sex_male,
                  Embarked_Q, Embarked_S
                  → Sex_female, Embarked_C 누락!
```

**해결 (실무 방법):**

```python
# 모델이 기대하는 컬럼 자동으로 가져오기
expected_cols = model.feature_names_in_

# 빠진 컬럼 자동으로 0 채우기
for col in expected_cols:
    if col not in new_passenger.columns:
        new_passenger[col] = 0

# 컬럼 순서 맞추기
new_passenger = new_passenger[expected_cols]
```

**왜 실무 방법인가?:**

```
하드코딩 → 전처리 바뀌면 수동 수정 필요
자동화   → 모델이 스스로 필요한 컬럼 알려줌

백엔드 비유:
하드코딩 = API 스펙 직접 작성
자동화   = Swagger에서 스펙 자동으로 읽어오기
```

**Day 3 연결:**

```
"get_dummies는 프로덕션에서 위험하다"
→ 오늘 직접 에러로 체감!
→ OneHotEncoder 쓰면 이 문제 자동 해결

면접 답변:
"get_dummies 쓰다가 Feature Mismatch 직접 경험
 → OneHotEncoder로 바꾼 이유 생김"
```

### 예측 결과 검증

```
3등칸 남성 (25세, Fare 7.5):
→ 사망 ❌ (100%) ← 타이타닉 역사와 일치

1등칸 여성 (25세, Fare 100):
→ 생존 ✅ (99%) ← 타이타닉 역사와 일치

"여성과 아이 먼저" 구조 원칙이
모델에 반영됨!
```

---

## 실습 3: 모델 비교 (compare_models.py)

### 결과

| 모델                | Accuracy | F1-Score |
| ------------------- | -------- | -------- |
| Logistic Regression | 0.7933   | 0.7132   |
| Decision Tree       | 0.8045   | 0.7407   |
| Random Forest       | 0.8268   | 0.7597   |

**최고 성능: Random Forest (F1: 0.7597)**

### 왜 이런 결과가 나왔나?

**Logistic Regression이 약한 이유:**

```
선형 경계로만 분류
→ "이 선 위면 생존, 아래면 사망"
→ 타이타닉은 복잡한 조건 조합
   (여성 AND 1등칸 AND 어린이)
→ 직선 하나로 못 나눔

백엔드 비유:
if (score > 50) return true  ← 단순 조건 하나
```

**Random Forest가 좋은 이유:**

```
나무 100개가 각각 다른 관점에서 투표
→ 한 나무가 틀려도 나머지가 커버
→ 복잡한 조건 조합 학습 가능

백엔드 비유:
로드밸런서 + 서버 100대
→ 1대 죽어도 나머지가 처리!
```

### 모델 선택 기준

```
단순 Accuracy가 아니라 F1-Score 기준으로 선택
이유: 불균형 데이터 (생존 38%, 사망 62%)
     → Accuracy의 함정 방지
```

**실무 선택 기준 5가지:**

```
1. 성능 (F1-Score)
2. 속도 (추론 시간 - 서빙 관점!)
3. 해석 가능성 (금융/의료는 필수)
4. 데이터 크기
5. 유지보수 (팀이 이해할 수 있나?)
```

---

## [WHAT IF] random_state 실험

**실험:**

```
random_state=42 고정:
→ 매번 동일한 결과 (Accuracy: 0.8268)

random_state 제거:
→ 실행마다 다른 결과
   1회: 0.8212
   2회: 0.8380
   3회: 0.8156
```

**결론:**

```
random_state = 재현성을 위한 seed 고정

실무 패턴:
# config.py
RANDOM_STATE = 42  # 프로젝트 전체 통일

→ 어떤 숫자든 상관없음
  "통일"이 핵심!

Cross Validation 때도 고정:
→ 동일 조건에서 모델 비교 가능
→ "이 결과가 운인지 실력인지" 판단 가능
```

---

## Week 9 개선 아이디어 🔥

### Feature Engineering 개선

**현재:**

```
Age 결측치 → 전체 평균 (29.7세)
F1-Score: 0.7597
```

**개선 예정:**
내가 이전에 했을때는 가족관계도 결측치채울때 mr / ms 그리고 가족관계 를 나이로 유추해서
나이 결측치도 채우고 햇엇는데 그래서 타이타닉 우선 구조가 가족단위엿던걸로 기억나서 햇던 기억이 나네
여자 와 아이가 보트 태우는 1순위엿는데

```
Name에서 호칭(Title) 추출:
Mr. → 성인 남성 평균
Mrs. → 기혼 여성 평균
Master → 남자 아이 평균

SibSp + Parch → FamilySize 파생 변수

예상 F1-Score: 0.82~0.85
```

**왜 개선될 것으로 예상?:**

```
타이타닉 실제 구조 원칙
"여성과 아이 먼저" → 데이터에 반영
호칭으로 성별/나이 더 정확하게 파악
```

**포트폴리오 스토리:**

```
"처음엔 단순 평균으로 결측치 처리
 → 호칭별 평균으로 개선
 → F1 0.76 → 0.83 향상
 → 도메인 지식이 모델 성능에 미치는 영향 체감"
```

---

## 오늘 핵심 요약

```
1. joblib compress 트레이드오프
   속도 vs 용량, 서빙은 compress=0

2. Feature Mismatch 에러 직접 체험
   → OneHotEncoder가 프로덕션에서 안전한 이유 체감

3. 평가 지표는 비즈니스 목적에 따라 달라짐
   같은 모델도 Recall/Precision/F1 선택이 다름

4. Random Forest = 앙상블 (다수결)
   복잡한 조건 조합 학습에 강함

5. random_state = 재현성 보장
   프로젝트 전체 config에서 통일 관리
```

---

**Next**: Day 5 - Docker로 오늘 만든 모델 컨테이너화 🐳
