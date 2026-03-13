# Day 23 강의 노트

**강의**: [P] Part4 Ch3-01~03 - 금융 이상 탐지 MLOps 파이프라인
**날짜**: 2026.03.13

---

## 오늘 들은 강의

✅ Part4 Ch3-01~03 - 금융 이상 탐지 커리큘럼, 환경 파악, 솔루션 선택

---

## 핵심 개념

### 1. 금융권 MLOps 제약 조건

- **망분리 규제**: 금융권은 외부 인터넷 접근 불가 → AWS/GCP 클라우드 사용 불가
- 따라서 **온프레미스(사내 서버) 기반** 스택 선택
  - GitLab (GitHub 대신, 사내 설치형)
  - Airflow (워크플로우 관리)
  - BentoML (모델 서빙)

### 2. Feature Store

```
Data Source → Processing → Feature Store → ML 모델
                              ↑
                    재사용 가능한 피처 저장소
                    (여러 모델이 공유)
```

- NestJS로 치면 **공통 서비스 모듈** - 여러 컨트롤러가 같은 서비스 재사용하는 것과 동일

### 3. 모델 선택 기준 (금융권)

- 금융권: **해석 가능성 > 성능**
- Logistic Regression 선호 (왜 이 거래가 이상한지 설명 가능)
- XGBoost, Neural Network는 블랙박스라 규제 통과 어려움

### 4. Surprise 라이브러리 (scikit-learn 비교)

|             | scikit-learn | surprise                    |
| ----------- | ------------ | --------------------------- |
| 입력        | X, y 분리    | (user, item, rating) 3개    |
| 데이터 변환 | 없음         | Reader → Dataset → trainset |
| 예측 단위   | 배치         | 한 쌍씩 predict(uid, iid)   |
| 평가지표    | accuracy, f1 | RMSE, MAE (평점 오차)       |

```python
# scikit-learn 방식
model.fit(X_train, y_train)
preds = model.predict(X_test)  # 배치

# surprise 방식
reader = Reader(rating_scale=(0.5, 5.0))  # 평점 범위 명시 필수
dataset = Dataset.load_from_df(df[["userId", "movieId", "rating"]], reader)
trainset, testset = train_test_split(dataset, test_size=0.2)
model.fit(trainset)
pred = model.predict(uid="1", iid="50")  # 한 쌍씩
print(pred.est)  # 예측 평점
```

- 구조는 sklearn 따라했지만, **추천 도메인 특성상 데이터 포맷이 다름**
- `Reader`: 평점 범위를 모델에게 알려주는 역할 (DTO 같은 개념)
- `trainset`: surprise 내부 포맷으로 변환된 객체 (바로 DataFrame 못 씀)

---

## 백엔드 연결

```
Surprise Reader    = DTO (데이터 형식 정의)
trainset           = DB Entity (ORM 변환된 객체)
model.predict(uid, iid) = findOne(userId, movieId)
RMSE               = API 응답 오차율 (낮을수록 좋음)
Feature Store      = 공통 서비스 모듈 (재사용 가능한 피처)
```

---

## 💡 핵심 포인트

- Airflow TaskFlow API: `@task` 데코레이터로 함수 = Task
- XCom: Task 간 데이터 전달 (return값 자동 저장)
- `bytes → hex string`: pickle 직렬화 객체를 XCom(JSON)으로 전달하기 위한 변환 필요
- `float("inf")`: 첫 학습 시 best_rmse 초기값 (무조건 저장되게)
