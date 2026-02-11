# Day 3 실습 노트

## 실습 2: 데이터 전처리

### 배운 것

#### 1. Chained Assignment 문제

preprocessiong.py 파일에 해당 내용들을 주석으로 실습하면서 작성 후 정리

**문제 상황**:

```python
# ⚠️ 경고 발생
df["Age"].fillna(..., inplace=True)
```

**해결 방법**:

```python
# ✅ 명시적 할당
df["Age"] = df["Age"].fillna(df["Age"].mean())
```

**왜 이렇게?**:

- pandas가 원본인지 복사본인지 헷갈림
- 명시적 할당이 가장 안전

**백엔드 비유**:

- 참조 vs 복사본 개념과 비슷

**참고 링크**:

- [pandas Chained Assignment 문서](링크)

---

#### 2. get_dummies vs OneHotEncoder

**발견한 문제**:

- get_dummies: 새 값 생성 → 차원 불일치
- OneHotEncoder: 즉시 에러 → 디버깅 쉬움

**코드 비교**:

```python
# get_dummies (EDA용)
df = pd.get_dummies(df, columns=['Sex'])

# OneHotEncoder (프로덕션용)
from sklearn.preprocessing import OneHotEncoder
encoder = OneHotEncoder(handle_unknown='ignore')
X = encoder.fit_transform(df[['Sex']])
```

**실무 선택 기준**:

- EDA/실험: get_dummies (빠름)
- 프로덕션: OneHotEncoder (안전)

**추가 실험**:

- [ ] OneHotEncoder handle_unknown 옵션 테스트
- [ ] 메모리 사용량 비교

---

#### 3. bool vs int 타입

**발견**:

```python
df = pd.get_dummies(df, columns=['Sex'])
print(df['Sex_male'].dtype)  # bool 타입!
```

**해결**:

```python
df[['Sex_male']] = df[['Sex_male']].astype(int)
```

**왜 int로 변환?**:

1. 파이프라인 안정성
2. 타입 스펙 명확
3. 디버깅 쉬움

**메모리 차이**:

- bool: 1 byte
- int64: 8 bytes
- 하지만 명확성이 더 중요!

**더 나은 방법**:

```python
df = pd.get_dummies(df, dtype=int)  # 바로 int로!
```

---

#### 4. StandardScaler 정규화

**코드**:

```python
scaler = StandardScaler()
df[['Age', 'Fare']] = scaler.fit_transform(df[['Age', 'Fare']])
```

**주의사항**:

- Train/Test 분리 시: fit은 train만!
- Scaler 저장 필요 (서빙 때 재사용)

**실무 패턴**:

```python
# 학습 시
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)

# 테스트 시
X_test_scaled = scaler.transform(X_test)

# 저장
import joblib
joblib.dump(scaler, 'scaler.pkl')
```

---

### 막혔던 부분

#### mode()[0] 사용 이유

**궁금했던 점**:

```python
df['Embarked'].fillna(df['Embarked'].mode()[0])
# 왜 [0]?
```

**답**:

- mode()는 Series 반환 (최빈값이 여러 개일 수 있어서)
- [0]으로 첫 번째 값 추출

**실험**:

```python
data = ['A', 'A', 'B', 'B']
mode = pd.Series(data).mode()
print(mode)  # ['A', 'B']
print(mode[0])  # 'A'
```

---

### 개선 아이디어

#### 1. 함수로 분리

```python
def handle_missing_values(df):
    """결측치 처리"""
    df["Age"] = df["Age"].fillna(df["Age"].mean())
    df['Embarked'] = df['Embarked'].fillna(df['Embarked'].mode()[0])
    return df
```

#### 2. Config 파일 관리

- DROP_COLS = ['Cabin', 'Ticket', 'Name']
- NUMERIC_COLS = ['Age', 'Fare']

#### 3. 로깅 추가

- 각 단계마다 logger.info()

---

### 다음에 해볼 것

- [ ] OneHotEncoder 실습
- [ ] Scaler 저장/로드 실습
- [ ] 전체 파이프라인 함수화

---

## 🚀 나중에 개선할 것 (포트폴리오 때!)

### 함수 분리 예시

```python
def handle_missing_values(df):
    df["Age"] = df["Age"].fillna(df["Age"].mean())
    return df
```

### Config 관리 예시

```python
# config.py
DROP_COLS = ['Cabin', 'Ticket', 'Name']
NUMERIC_COLS = ['Age', 'Fare']
```

### 로깅 예시

```python
logger.info("결측치 처리 완료")
```

## 실습 3: Class Imbalance 확인

### 배운 것

#### 1. Class Imbalance 비율 기준

**정해진 기준은 없지만 일반적으로:**

| 비율  | 상태 |
| ----- | ---- |
| 50:50 | 균형 |
| 60:40 | 경미 |
| 80:20 | 중간 |
| 95:5  | 심각 |

**타이타닉 결과:**

```python
Not Survived (0): 549명 (61.6%)
Survived (1):     342명 (38.4%)
Imbalance Ratio: 1.60 → "경미" 수준
→ 별도 처리 불필요!
```

---

#### 2. value_counts() 활용법

**코드:**

```python
# 갯수
df['Survived'].value_counts()

# 비율 (normalize=True 추가)
df['Survived'].value_counts(normalize=True)
```

**왜 둘 다 보나?:**

- 갯수만 보면 규모 파악 가능
- 비율까지 봐야 불균형 판단 가능
- 실무에서 항상 같이 확인!

---

#### 3. matplotlib 기본 패턴

**이번에 쓴 패턴:**

```python
plt.figure(figsize=(8, 6))   # 캔버스 크기
df['Survived'].value_counts().plot(kind='bar')  # 그래프 종류
plt.title("제목")             # 제목
plt.xlabel("x축 이름")        # x축
plt.ylabel("y축 이름")        # y축
plt.xticks([0,1], ['라벨1', '라벨2'], rotation=0)  # x축 라벨
plt.tight_layout()            # 여백 자동 조절
plt.savefig('파일명.png')     # 저장
```

**현재 이해 수준:**

- 코드 보면 뭐하는지 이해 가능 ✅
- 처음부터 혼자 작성은 아직 어려움
- 반복하면서 익히는 중!

---

#### 4. 파일 저장 경로 개선

**문제:**

```python
# ⚠️ 실행 위치에 따라 저장 위치 달라짐
plt.savefig('class_distribution.png')
```

**해결:**

```python
# ✅ 항상 같은 폴더에 저장
save_path = os.path.join(BASE_DIR, 'class_distribution.png')
plt.savefig(save_path)
```

**왜?:**

- 어디서 실행해도 동일한 위치에 저장
- 실습 2에서 배운 패턴 그대로 적용!

---

### 막혔던 부분

#### 없음! 비교적 순탄하게 진행

- 실습 2에서 배운 패턴 재사용
- matplotlib은 코드 보고 이해하는 수준으로 진행

---

```

```
