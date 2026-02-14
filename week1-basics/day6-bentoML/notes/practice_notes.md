# Day 6 실습 노트 - BentoML 모델 서빙

> 날짜: 2026-02-14  
> 목표: Titanic 모델을 BentoML로 API 서버화

---

## 실습 흐름 요약

```
best_model.pkl (Day 4)
    ↓ bentoml.sklearn.save_model()
BentoML ModelStore
    ↓ to_runner()
Runner (모델 실행 엔진)
    ↓ bentoml.Service()
Service (API 서버)
    ↓ bentoml serve
localhost:3000/predict
    ↓ curl POST
{"survived": 1, "message": "1= 생존, 0 = 사망"}
```

---

## Step 1: 환경 세팅

```bash
# conda 환경 확인
conda info --envs
# mlops-study 환경 활성화 상태 확인

# BentoML 설치
pip install bentoml==1.1.11

# 버전 확인
bentoml --version
# bentoml, version 1.1.11
```

**폴더 구조:**

```
day6-bentoml/
├── notes/
│   ├── lecture_notes.md
│   └── practice_notes.md   ← 이 파일
├── outputs/
│   └── best_model.pkl      ← Day 4에서 복사
├── src/
│   ├── save_model.py
│   └── service.py
└── requirements.txt
```

---

## Step 2: ModelStore에 모델 등록 (save_model.py)

```python
import bentoml
import joblib

# best_model.pkl 로드
model = joblib.load("outputs/best_model.pkl")

# BentoML ModelStore에 등록
saved_model = bentoml.sklearn.save_model("titanic_model", model)
print(f"모델 저장 완료: {saved_model}")
```

```bash
python src/save_model.py
# 모델 저장 완료: Model(tag="titanic_model:tmdmbaajss4rhzus")

# 등록 확인
bentoml models list
```

**핵심 개념:**

- `bentoml.sklearn.save_model()` → ModelStore(`~/.bentoml/models/`)에 저장
- 자동으로 고유 태그(tmdmbaajss4rhzus) 생성 → 버전 관리
- `bentoml models list` → npm list -g 와 같은 개념

---

## Step 3: service.py 작성

```python
import bentoml
import pandas as pd
from bentoml.io import JSON

# ModelStore에서 최신 버전 로드 → Runner 생성
runner = bentoml.sklearn.get("titanic_model:latest").to_runner()

# Service 정의
svc = bentoml.Service("titanic_service", runners=[runner])

# 학습 때 컬럼 순서 (순서 다르면 에러!)
EXPECTED_COLUMNS = [
    "Pclass", "Age", "SibSp", "Parch", "Fare",
    "Sex_female", "Sex_male",
    "Embarked_C", "Embarked_Q", "Embarked_S"
]

@svc.api(input=JSON(), output=JSON())
async def predict(input_data) -> dict:
    # 입력 데이터 → DataFrame 변환
    # [input_data]로 감싸면 행 1개짜리 테이블이 됨
    features = pd.DataFrame([input_data])

    # 컬럼 순서 강제 정렬 (학습 때와 동일하게)
    features = features[EXPECTED_COLUMNS]

    # 비동기 예측
    result = await runner.predict.async_run(features)

    # sklearn predict 결과는 배열 → result[0]으로 첫 번째 값 추출
    return {
        "survived": int(result[0]),
        "message": "1 = 생존, 0 = 사망"
    }
```

---

## Step 4: 서버 실행 & 테스트

```bash
# 서버 실행
bentoml serve src/service.py:svc --reload
# → http://localhost:3000 (Swagger UI 자동 생성!)
```

**생존 케이스 테스트 (1등석 + 여성 + 30세):**

```bash
curl -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Pclass": 1, "Age": 30, "SibSp": 0, "Parch": 0, "Fare": 100,
    "Sex_female": 1, "Sex_male": 0,
    "Embarked_C": 1, "Embarked_Q": 0, "Embarked_S": 0
  }'
# 결과: {"survived": 1, "message": "1 = 생존, 0 = 사망"}
```

**사망 케이스 테스트 (3등석 + 남성 + 25세):**

```bash
curl -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Pclass": 3, "Age": 25, "SibSp": 0, "Parch": 0, "Fare": 7,
    "Sex_female": 0, "Sex_male": 1,
    "Embarked_C": 0, "Embarked_Q": 0, "Embarked_S": 1
  }'
# 결과: {"survived": 0, "message": "1 = 생존, 0 = 사망"}
```

---

## 트러블슈팅

### 에러 1: Feature names missing

```
ValueError: Feature names seen at fit time, yet now missing:
- Embarked_C
- Sex_female
```

**원인:** 학습 때 `pd.get_dummies(drop_first=False)` 사용 → 모든 컬럼 존재  
**해결:** curl 요청에 `Sex_female`, `Embarked_C` 추가

### 에러 2: Feature names must be in the same order

```
ValueError: Feature names must be in the same order as they were in fit.
```

**원인:** curl로 보낸 컬럼 순서 ≠ 학습 때 컬럼 순서  
**해결:** `EXPECTED_COLUMNS` 리스트로 강제 정렬

```python
# 모델의 실제 컬럼 순서 확인 방법
import joblib
model = joblib.load("outputs/best_model.pkl")
print(model.feature_names_in_)
```

---

## 오늘 배운 핵심

```
1. BentoML = ML 모델을 위한 API 프레임워크
   (NestJS에서 Controller + Service 구조와 동일)

2. ModelStore = 모델 버전 관리 시스템
   (npm global registry 개념)

3. Runner = 모델 실행 엔진 (NestJS의 Service)
   Service = API 서버 (NestJS의 Controller)

4. 비동기 서빙 가능 (async/await)
   → runner.predict.async_run()

5. 지금은 로컬 서버 (터미널 켜있을 때만 동작)
   → 다음 단계: Docker 패키징 → 클라우드 배포
```
