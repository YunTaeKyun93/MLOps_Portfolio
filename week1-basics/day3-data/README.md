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
- [ ] CSV 파일 읽기 (`pd.read_csv()`)
- [ ] 데이터 크기 확인 (`df.shape`)
- [ ] 컬럼 정보 확인 (`df.info()`)
- [ ] 처음 5개 행 보기 (`df.head()`)
- [ ] 통계 정보 확인 (`df.describe()`)
- [ ] 결측치 확인 (`df.isnull().sum()`)

### 실행 결과

```bash
# 예시 출력 (실습 후 작성)
📊 데이터 크기: (891, 12)
📋 컬럼 정보:
...
```

---

### 실습 2: 데이터 전처리 (결측치, 정규화)

- [ ] `preprocessing.py` 파일 생성
- [ ] 결측치 처리
  - [ ] 수치형: 평균값으로 채우기 (`fillna()`)
  - [ ] 범주형: 최빈값으로 채우기
  - [ ] 불필요한 컬럼 삭제 (`drop()`)
- [ ] 범주형 → 수치형 변환
  - [ ] One-Hot Encoding (`pd.get_dummies()`)
- [ ] 정규화
  - [ ] StandardScaler 사용
- [ ] 전처리된 데이터 저장

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

- [ ] `class_imbalance.py` 파일 생성
- [ ] 타겟 분포 확인 (`value_counts()`)
- [ ] 비율 확인 (`value_counts(normalize=True)`)
- [ ] 막대 그래프 시각화 (`matplotlib`)
- [ ] Imbalance Ratio 계산
- [ ] 그래프 저장 (`class_distribution.png`)

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

- [ ] `pandas_basic.py`: 데이터 탐색
- [ ] `preprocessing.py`: 전처리
- [ ] `class_imbalance.py`: 불균형 체크
- [ ] `train_preprocessed.csv`: 전처리된 데이터
- [ ] `class_distribution.png`: 시각화 결과

### 스크린샷

## (실습 후 추가)

```
class_distribution.png
```

:

---

## 🤔 오늘의 회고

### 배운 것 (3가지)

1. (실습 후 작성)
2. (실습 후 작성)
3. (실습 후 작성)

### 백엔드 개발자 관점에서 연결된 것

1. (실습 후 작성)
2. (실습 후 작성)

### 막혔던 부분

1. (실습 후 작성)
   - 해결 방법: (실습 후 작성)

### 내일 보완할 것

1. (실습 후 작성)

---

## ⏱️ 시간 기록

- **강의 시청**: **시간 **분
- **실습**: **시간 **분
- **회고 작성**: \_\_분
- **총 소요**: **시간 **분

---

## 💬 Claude에게 질문

### 질문 1

(실습 중 막힌 부분이나 궁금한 점을 여기에 작성하세요!)

### 질문 2

(추가 질문)

---

## 🔗 참고 자료

- [pandas 공식 문서](https://pandas.pydata.org/docs/)
- [scikit-learn Preprocessing](https://scikit-learn.org/stable/modules/preprocessing.html)
- [Kaggle Titanic Dataset](https://www.kaggle.com/c/titanic)

---

## 📝 다음 할 일 (Day 4 미리보기)

- [ ] [P] Part 2 - Ch 1-15~18 (모델 학습 및 평가)
- [ ] scikit-learn으로 간단한 분류 모델 학습
- [ ] 모델 저장 (.pkl 파일)

---

**Last Updated**: 2024.XX.XX

**Status**: 강의 완료 ✅ | 실습 진행 중 🔄
