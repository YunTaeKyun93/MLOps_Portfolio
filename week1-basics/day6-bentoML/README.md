# Day 6 - BentoML 모델 서빙

> **목표:** Day 4에서 만든 Titanic 모델을 BentoML로 API 서버화  
> **핵심:** ML 모델 → HTTP API 엔드포인트

---

## 학습 목표

- [ ] BentoML 개념 이해 (Runner / Service / Bento)
- [ ] ModelStore에 모델 등록
- [ ] service.py 작성
- [ ] 로컬 서빙 실행
- [ ] curl로 예측 요청

---

## BentoML이란?

### 한 줄 정의

> ML 모델을 위한 API 서버 프레임워크  
> = "ML 모델을 위한 NestJS"

### 왜 FastAPI 말고 BentoML?

| 항목          | FastAPI        | BentoML                   |
| ------------- | -------------- | ------------------------- |
| 모델 로드     | 직접 코드 작성 | 자동 처리                 |
| API 문서      | 직접 설정      | Swagger 자동 생성         |
| Docker 이미지 | 직접 작성      | bentoml build로 자동 생성 |
| 버전 관리     | 없음           | ModelStore로 내장         |
| 배치 처리     | 직접 구현      | 내장                      |

---

## 핵심 개념 3가지

### 1. Runner (모델 실행 엔진)

```python
runner = bentoml.sklearn.get("titanic_model:latest").to_runner()
```

- NestJS의 **Service 클래스**와 동일한 역할
- 모델을 실제로 실행하는 단위
- `async_run()` 으로 비동기 추론 가능
- BentoML이 내부적으로 스레드풀, 배치 처리 등을 자동으로 관리

**동작 원리:**

```
API 요청 → Service → Runner → 모델 추론 → 결과 반환
```

### 2. Service (API 서버)

```python
svc = bentoml.Service("titanic_service", runners=[runner])

@svc.api(input=JSON(), output=JSON())
async def predict(input_data) -> dict:
    ...
```

- NestJS의 **Controller**와 동일한 역할
- `@svc.api` 데코레이터로 엔드포인트 정의
- `input=JSON(), output=JSON()` → 입출력 타입 지정
- Swagger UI 자동 생성 (http://localhost:3000)

### 3. Bento (배포 단위)

```bash
bentoml build         # Bento 생성
bentoml containerize  # Docker 이미지로 변환
```

- 모델 + 코드 + 환경(requirements) 을 하나로 묶은 패키지
- Docker 이미지라고 생각하면 됨
- Day 7~8에서 학습 예정

---

## ModelStore 개념

### 구조

```
~/.bentoml/models/
└── titanic_model/
    └── tmdmbaajss4rhzus/    ← 자동 생성된 버전 태그
        ├── saved_model.pkl
        └── model_meta.json
```

### 백엔드 비유

```
best_model.pkl       = 로컬 파일 (프로젝트 내부)
BentoML ModelStore   = npm global registry

# 저장
bentoml.sklearn.save_model("titanic_model", model)  # = npm install -g

# 조회
bentoml models list                                  # = npm list -g
bentoml.sklearn.get("titanic_model:latest")          # = require('package')
```

### 버전 관리

```bash
bentoml models list
# titanic_model:tmdmbaajss4rhzus  ← v1 (처음 학습)
# titanic_model:abc123xyz          ← v2 (재학습 후)

# 특정 버전 사용
bentoml.sklearn.get("titanic_model:tmdmbaajss4rhzus")

# 최신 버전 사용
bentoml.sklearn.get("titanic_model:latest")
```

---

## 전체 코드 흐름

### save_model.py

```python
import bentoml
import joblib

model = joblib.load("outputs/best_model.pkl")
saved_model = bentoml.sklearn.save_model("titanic_model", model)
print(f"저장 완료: {saved_model}")
```

### service.py

```python
import bentoml
import pandas as pd
from bentoml.io import JSON

runner = bentoml.sklearn.get("titanic_model:latest").to_runner()
svc = bentoml.Service("titanic_service", runners=[runner])

EXPECTED_COLUMNS = [
    "Pclass", "Age", "SibSp", "Parch", "Fare",
    "Sex_female", "Sex_male",
    "Embarked_C", "Embarked_Q", "Embarked_S"
]

@svc.api(input=JSON(), output=JSON())
async def predict(input_data) -> dict:
    features = pd.DataFrame([input_data])
    features = features[EXPECTED_COLUMNS]
    result = await runner.predict.async_run(features)
    return {
        "survived": int(result[0]),
        "message": "1 = 생존, 0 = 사망"
    }
```

---

## 실행 방법

```bash
# 1. 모델 등록
python src/save_model.py

# 2. 서버 실행
bentoml serve src/service.py:svc --reload

# 3. 생존 케이스 테스트 (1등석 + 여성)
curl -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Pclass": 1, "Age": 30, "SibSp": 0, "Parch": 0, "Fare": 100,
    "Sex_female": 1, "Sex_male": 0,
    "Embarked_C": 1, "Embarked_Q": 0, "Embarked_S": 0
  }'
# → {"survived": 1, "message": "1 = 생존, 0 = 사망"}

# 4. 사망 케이스 테스트 (3등석 + 남성)
curl -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Pclass": 3, "Age": 25, "SibSp": 0, "Parch": 0, "Fare": 7,
    "Sex_female": 0, "Sex_male": 1,
    "Embarked_C": 0, "Embarked_Q": 0, "Embarked_S": 1
  }'
# → {"survived": 0, "message": "1 = 생존, 0 = 사망"}
```

---

## 현재 단계 vs 다음 단계

```
현재 (Day 6):
로컬 서버
  bentoml serve → localhost:3000
  터미널 켜있을 때만 동작
  외부 접근 불가

다음 (Day 7~8):
Docker + 클라우드 배포
  bentoml build → Docker 이미지
  어디서든 실행 가능
  항상 켜있는 서버
  외부에서 접근 가능
```

---

## 폴더 구조

```
day6-bentoml/
├── notes/
│   ├── lecture_notes.md    ← 강의 내용 정리
│   └── practice_notes.md   ← 실습 기록
├── outputs/
│   └── best_model.pkl      ← Day 4에서 복사
├── src/
│   ├── save_model.py       ← ModelStore 등록
│   └── service.py          ← API 서버 정의
├── requirements.txt
└── README.md               ← 이 파일
```

---

## 참고

- Day 4: Titanic 모델 학습 (best_model.pkl 생성)
- Day 5: Docker 기초 학습
- Day 7~8: Docker 이미지 생성 + 클라우드 배포 예정
