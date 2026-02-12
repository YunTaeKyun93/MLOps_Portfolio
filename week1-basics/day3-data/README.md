# Day3_README

# 📅 Day 3: 학습 데이터 준비

**날짜**: 2024.XX.XX

**소요 시간**: 약 7시간

**강의**: [P] Part 2 - Chapter 1 (01-02 ~ 01-06)

---

## 🎯 오늘의 목표

### 핵심 질문

- [ ] 데이터 샘플링은 왜 필요한가?
- [ ] Labeling이란 무엇이고, 왜 ML에서 가장 비싼 작업인가?
- [ ] Class Imbalance 문제와 해결 방법은?
- [ ] pandas로 CSV 데이터를 어떻게 다루나?

### 백엔드 관점 연결

```
데이터 전처리 = API 미들웨어
결측치 처리 = Null check + Default value
정규화 = 데이터 포맷 통일
One-Hot Encoding = Enum → Integer 변환
Class Imbalance = 트래픽 편중 문제
```

---

## 💻 실습 체크리스트

### 실습 환경 설정

- [x] Kaggle 계정 생성
- [x] Kaggle API 토큰 설정 (`~/.kaggle/kaggle.json`)
- [x] 데이터셋 다운로드 (Titanic 또는 House Prices)

---

### 실습 1: CSV 데이터 읽기 및 기본 탐색

- [x] `pandas_basic.py` 파일 생성
- [x ] CSV 파일 읽기 (`pd.read_csv()`)
- [x ] 데이터 크기 확인 (`df.shape`)
- [x ] 컬럼 정보 확인 (`df.info()`)
- [x ] 처음 5개 행 보기 (`df.head()`)
- [x ] 통계 정보 확인 (`df.describe()`)
- [x] 결측치 확인 (`df.isnull().sum()`)

### 실행 결과

```bash
# 예시 출력 (실습 후 작성)
📊 데이터 크기: (891, 12)
📋 컬럼 정보:
...
```

---

### 실습 2: 데이터 전처리 (결측치, 정규화)

- [x] `preprocessing.py` 파일 생성
- [x] 결측치 처리
  - [x] 수치형: 평균값으로 채우기 (`fillna()`)
  - [x] 범주형: 최빈값으로 채우기
  - [x] 불필요한 컬럼 삭제 (`drop()`)
- [x] 범주형 → 수치형 변환
  - [x] One-Hot Encoding (`pd.get_dummies()`)
- [x] 정규화
  - [x] StandardScaler 사용
- [x] 전처리된 데이터 저장

### 실행 결과

```bash
# 예시 출력 (실습 후 작성)
✅ 결측치 처리 완료
✅ 범주형 변환 완료
✅ 정규화 완료
💾 전처리된 데이터 저장 완료!
```

---

### 실습 3: Class Imbalance 확인 및 시각화

- [x] `class_imbalance.py` 파일 생성
- [x] 타겟 분포 확인 (`value_counts()`)
- [x] 비율 확인 (`value_counts(normalize=True)`)
- [x] 막대 그래프 시각화 (`matplotlib`)
- [x] Imbalance Ratio 계산
- [x] 그래프 저장 (`class_distribution.png`)

### 실행 결과

```bash
# 예시 출력 (실습 후 작성)
🎯 타겟(Survived) 분포:
0    549
1    342

⚖️ Imbalance Ratio: 1.61
✅ Class Imbalance 양호
```

---

## 📊 실습 결과물

### 생성된 파일

- [x] `pandas_basic.py`: 데이터 탐색
- [x] `preprocessing.py`: 전처리
- [x] `class_imbalance.py`: 불균형 체크
- [x] `train_preprocessed.csv`: 전처리된 데이터
- [x] `class_distribution.png`: 시각화 결과

###

## (실습 후 추가)

outputs에 추가 함

```
class_distribution.png
```

:

---

### 오늘 전체 회고

**잘한 것:**

1. Chained Assignment 문제 직접 발견 & 해결
2. get_dummies vs OneHotEncoder 차이 파악
3. 비율표 직접 찾아서 정리

**아쉬운 것:**

1. matplotlib 아직 처음부터 못 씀
2. 실습 속도가 예상보다 느렸음

## 💬 Claude에게 질문

### 질문 1

오늘은 따로 없었고, 파일 구조화나 지금 템플릿을 많이 변경했는데, 이에 대한 조언

### 질문 2

단순히 int bool으로도 생각할게 많았고, 더 공부할수 있게되어서 좋았다

---

## 📝 다음 할 일 (Day 4 미리보기)

- [ ] [P] Part 2 - Ch 1-15~18 (모델 학습 및 평가)
- [ ] scikit-learn으로 간단한 분류 모델 학습
- [ ] 모델 저장 (.pkl 파일)

---

**Last Updated**: 2026.02.12

**Status**: 강의 완료 ✅ | 실습 완료 ✅
