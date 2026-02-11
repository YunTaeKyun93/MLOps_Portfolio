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

## 📚 강의 수강 체크리스트

### ✅ 01-02. 학습 데이터 준비 1 (Data 유형) - 27분

- [x] **강의 시청 완료**
- [x] **핵심 개념 정리**

### 주요 내용

- **정형 데이터 (Structured Data)**:
  - 표 형태 (행/열)
  - 예: CSV, 데이터베이스
  - 백엔드의 RDBMS와 비슷
- **비정형 데이터 (Unstructured Data)**:
  - 이미지, 텍스트, 오디오, 비디오
  - 예: 사진, 리뷰 텍스트
  - NoSQL, Object Storage와 비슷
- **반정형 데이터 (Semi-structured Data)**:
  - JSON, XML
  - 백엔드 API 응답과 동일!

### 백엔드 개발자 관점

```
정형 데이터 = PostgreSQL 테이블
비정형 데이터 = S3에 저장된 파일
반정형 데이터 = API JSON Response
```

### 질문 & 답변

- **Q**: 정형 데이터와 비정형 데이터의 차이는?
- **A**: 정형데이터는 표와 같이 되어있는 데이터 형태이고 비정형은 이미지나 텍스트 오디오 등과 같이 정형화 되어있지않은 데이터
- **Q**: 왜 데이터 유형에 따라 전처리 방법이 다른가?
- **A**: 데이터 유형에 따라 데이터의 정보의 밀도가 다르기 때문에 ??
- 보완 답변
  정답에 가까워요! 조금 더 구체적으로:
  1. 정형 데이터 (Tabular):
     - 숫자/범주로 명확히 정의됨
     - 전처리: 결측치 채우기, 정규화, 인코딩
     - 예: Age 컬럼 → 평균으로 채움
  2. 비정형 데이터 (이미지):
     - 픽셀 값 (0~255)
     - 전처리: 리사이징, 정규화(0~1), 증강(Augmentation)
     - 예: 이미지 크기 통일, 회전/반전
  3. 비정형 데이터 (텍스트):
     - 단어/문장
     - 전처리: 토큰화, 불용어 제거, 임베딩
     - 예: "I love ML" → [1, 523, 87] (숫자로 변환)
  → 데이터 형태가 다르니 "숫자로 만드는 방법"도 다름!

---

### ✅ 01-03. 학습 데이터 준비 2 (Data Sampling) - 9분

- [x] **강의 시청 완료**
- [x] **핵심 개념 정리**

### 주요 내용

- **전체 데이터를 다 쓰지 않는 이유**:
  - 계산 비용 절감
  - 빠른 프로토타이핑
  - 대표성만 확보되면 충분
- **샘플링 방법**:
  - Random Sampling (무작위)
  - Stratified Sampling (계층별)
  - Time-based Sampling (시간 기반)

### 백엔드 개발자 관점

```
샘플링 = SQL의 LIMIT + WHERE
대용량 데이터 = 페이지네이션과 비슷
대표성 확보 = A/B 테스트의 샘플 그룹 선정
```

### 질문 & 답변

- **Q**: 전체 데이터를 다 쓰지 않고 샘플링하는 이유는?
- **A**: 전체를 다하면 그만큼의 비용과 시간을 써야하기 때문에

- **Q**: Stratified Sampling이 필요한 경우는?
- **A**: 기준점을 만들고 원하는 컬럼(피처)을 기준으로 골고루 분배후 해야하니까 예를 들어 전연령의 데이터 샘플
- 보완
  정확해요! 예시를 추가하면:
  Stratified Sampling (계층별 샘플링)이 필요한 경우:
  1. Class Imbalance가 있을 때:
     - 전체 데이터: 남성 70%, 여성 30%
     - Random Sampling: 남성 90%, 여성 10% (편향!)
     - Stratified Sampling: 남성 70%, 여성 30% (비율 유지!)
  2. 소수 클래스를 놓치지 않으려고:
     - 전체 데이터: 정상 99%, 사기 1%
     - Random으로 10% 샘플링 → 사기 데이터 없을 수도!
     - Stratified로 샘플링 → 사기 데이터 1% 확보
  → 원본 데이터의 "비율"을 유지하면서 샘플링!

---

### ✅ 01-04. 학습 데이터 준비 3 (Labeling과 이에 따른 모델 학습 유형) - 45분

- [x] **강의 시청 완료**
- [x] **핵심 개념 정리**

### 주요 내용

- **Labeling (레이블링)**:
  - 데이터에 정답을 달아주는 작업
  - 예: 이미지에 “고양이”, “강아지” 태그
  - **가장 시간/비용이 많이 드는 작업!**
- **학습 유형**:
  1. **Supervised Learning (지도 학습)**: 정답 있음
     - 분류(Classification): 고양이 vs 강아지
     - 회귀(Regression): 집값 예측
  2. **Unsupervised Learning (비지도 학습)**: 정답 없음
     - 군집화(Clustering): 유사한 고객 그룹핑
  3. **Semi-Supervised Learning (준지도 학습)**: 일부만 정답
     - 정답 데이터 부족할 때

### 백엔드 개발자 관점

```
Labeling = 데이터 검증 + 태그 달기
Supervised = 테스트 케이스 있는 TDD
Unsupervised = 패턴 발견 (로그 분석)
```

### 질문 & 답변

- **Q**: Supervised Learning에서 Labeling이 왜 비싼가?
- **A**: 모든 데이터에 정답을 달아줘야하니까 그만큼의 시간과 리소스를 사용해야함
- **Q**: Labeling 비용을 줄이는 방법은?
- **A**: 준지도 학습을 해도 되구, threshold 나 앙상블등을 하여 채워넣는 것도 방법일까
- 보완
  좋은 방향이에요! 실무에서 쓰는 방법들:
  1. Semi-Supervised Learning (준지도 학습):
     - 일부만 라벨링, 나머지는 모델이 예측
     - 예: 1,000개만 라벨링, 나머지 9,000개는 모델이 채움
  2. Active Learning (능동 학습):
     - 모델이 "이거 애매한데?" 싶은 것만 사람이 라벨링
     - 예: 확신도 낮은 100개만 사람이 확인
  3. Weak Supervision (약한 지도):
     - 규칙 기반으로 자동 라벨링
     - 예: "가격 > 100만원" → 고가 제품 (자동 태그)
  4. Pre-trained Model 활용:
     - 이미 학습된 모델로 초벌 라벨링
     - 예: GPT로 텍스트 카테고리 자동 분류
  5. Crowdsourcing:
     - Amazon Mechanical Turk, Labelbox 등
     - 여러 사람이 나눠서 라벨링 → 비용↓ 속도↑

---

### ✅ 01-05. 학습 데이터 준비 4 (Class Imbalance) - 56분

- [x] **강의 시청 완료**
- [x] **핵심 개념 정리**

### 주요 내용

- **Class Imbalance (클래스 불균형)**:
  - 한쪽 클래스가 압도적으로 많은 경우
  - 예: 정상 거래 99%, 사기 거래 1%
  - 모델이 소수 클래스를 무시하는 문제
- **해결 방법**:
  1. **Oversampling**: 소수 클래스 복제 (SMOTE)
  2. **Undersampling**: 다수 클래스 줄이기
  3. **Class Weight**: 소수 클래스에 가중치
  4. **Ensemble**: 여러 모델 조합
- **평가 지표**:
  - Accuracy는 의미 없음!
  - Precision, Recall, F1-Score 사용

### 백엔드 개발자 관점

```
Class Imbalance = 트래픽 편중
99% 정상 요청, 1% 악의적 요청

해결:
- Rate Limiting (속도 제한)
- 로드 밸런싱
- 캐싱 전략
```

### 질문 & 답변

- **Q**: Class Imbalance가 왜 문제인가?
- **A**: 해당 데이터의 균형이 고르지 못하다면 학습을 제대로 할 수 가 없어서
- **Q**: SMOTE와 일반 Oversampling의 차이는?
- **A**: SMOTE가 거리안에 있는 유사한 데이터를 생성(복제??) 하는 개념으로 알고있는데 다른 Oversampling을 잘 모르겠음 ADASYAN은 해당 거리에 비례해서 갯수를 더 생성 하는건 알고있는데
- 보완
  거의 정답이에요! 차이점을 명확히:
  1. Random Oversampling (일반적인 방법):
     - 소수 클래스를 그대로 "복제"
     - 예: [1, 2, 3] → [1, 2, 3, 1, 2, 3] (똑같은 데이터 반복)
     - 단점: 과적합(Overfitting) 위험! 똑같은 패턴만 학습
  2. SMOTE (Synthetic Minority Over-sampling):
     - 기존 데이터 "사이"에 새로운 데이터 생성
     - 예:
       A = [1, 2]
       B = [3, 4]
       → 새 데이터 = [2, 3] (A와 B 사이)
     - 장점: 다양한 패턴 학습 가능
  시각화:
  Random Oversampling:
  ● ● ● (원본)
  ● ● ● ● ● ● (똑같은 거 복제)
  SMOTE:
  ● ● ● (원본)
  ● ◐ ● ◐ ● (사이에 새 데이터 생성)
- **Q**: Class Imbalance 해결 방법 3가지는?
- **A**: Over, Under Sampling과 앙상블, 등등
- 보완
  맞아요! 좀 더 구체적으로 5가지:
  1. Oversampling (소수 클래스 늘리기):
     - Random Oversampling
     - SMOTE
     - ADASYN (님이 아시는 것!)
  2. Undersampling (다수 클래스 줄이기):
     - Random Undersampling
     - Tomek Links (경계에 있는 것만 제거)
  3. Class Weight (가중치 조정):
     - 소수 클래스에 높은 가중치
     - sklearn: class_weight='balanced'
  4. Ensemble (앙상블):
     - 여러 모델 조합
     - Balanced Bagging, EasyEnsemble
  5. 평가 지표 변경:
     - Accuracy 버리고
     - Precision, Recall, F1-Score 사용

---

### ✅ 01-06. [실습 1] 학습 데이터 전체 실습 - 32분

- [x] **강의 시청 완료**
- [x] **실습 따라하기 완료**

### 실습 내용

- 강의에서 다룬 데이터셋: (강의 보고 작성)
- 사용한 라이브러리: (강의 보고 작성)
- 주요 코드: (강의 보고 작성)

### 질문 & 답변

- **Q**: 강의에서 다룬 데이터셋은 무엇이었나?
- **A**: sklearn의 load_iris과 winequality_for_class_imbalance,
- **Q**: 실습에서 가장 중요한 부분은?
- **A**: 간단한 데이터들로 위의 방법들 라벨링, 샘플링, 데이터 임발란스 해결 법들을 해봤는데,
  아직은 따라하면서 이해에 가까운 수준이라 만약 내가 실제 프로젝트에서 사용할때는 또 헷갈릴수도 있어서
  앞으로 계속 반복을 해야할듯 하다

1. 문제 발생: "Class Imbalance네?"
2. 검색: "sklearn class imbalance smote"
3. 문서 확인: sklearn 공식 문서
4. 코드 복붙: 내 데이터에 적용
5. 결과 확인: 성능 향상 체크

→ 처음부터 외울 필요 없어요!
→ "이런 게 있었지" 정도만 기억하면 충분!

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
