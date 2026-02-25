# Day 15 - GitHub Actions CI 트러블슈팅

## 발생한 문제들

### 1. pytest 명령어 없음

**에러**: `pytest: command not found`

**원인**: `requirements.txt`에 pytest가 없어서 CI 환경에 설치 안 됨

**해결**:

```yaml
- name: 패키지 설치
  run: |
    pip install -r requirements.txt
    pip install pytest httpx
```

---

### 2. pkl 파일 없음

**에러**: `No such file or directory: 'outputs/user_item_matrix.pkl'`

**원인**: `.gitignore`에 `*.pkl` 등록되어 있어서 GitHub에 pkl 없음

**해결**: CI에서 직접 모델 학습 step 추가

```yaml
- name: 모델 학습
  working-directory: week2-serving/day7-cf-recommender
  run: python src/train.py
```

---

### 3. 데이터 파일 없음

**에러**: `No such file or directory: 'data/ml-1m/ratings.dat'`

**원인**: `.gitignore`에 `data/` 등록되어 있어서 GitHub에 데이터 없음

**해결**: CI에서 데이터 다운로드 step 추가

```yaml
- name: 데이터 다운로드
  working-directory: week2-serving/day7-cf-recommender
  run: |
    mkdir -p data/ml-1m
    curl -O https://files.grouplens.org/datasets/movielens/ml-1m.zip
    unzip ml-1m.zip -d data/
```

---

### 4. outputs 폴더 없음

**에러**: `cp: target 'outputs/': No such file or directory`

**원인**: `.gitignore`로 인해 빈 폴더는 GitHub에 올라가지 않음

**해결**: CI에서 폴더 먼저 생성

```yaml
- name: outputs 폴더 생성
  run: mkdir -p week2-serving/day8-fastapi/outputs
```

---

## 앞으로 CI 만들 때 고려할 것

### 1. .gitignore 파일 확인

CI는 GitHub 서버에서 실행 → gitignore된 파일은 없음

- 데이터 파일 → CI에서 다운로드 step 추가
- pkl 파일 → CI에서 학습 step 추가
- 빈 폴더 → `mkdir -p` 로 생성

### 2. requirements.txt 분리

```
day7-cf-recommender/requirements.txt  ← 학습용
day8-fastapi/requirements.txt         ← 서빙용
```

역할별로 분리해서 CI에서 각각 설치

### 3. working-directory 주의

CI는 repo 루트에서 실행됨

```yaml
working-directory: week2-serving/day8-fastapi # 경로 명시 필요
```

### 4. paths 설정으로 불필요한 CI 실행 방지

```yaml
on:
  pull_request:
    branches: [main]
    paths:
      - "week2-serving/**"
      - ".github/workflows/**"
```

README 수정 같은 변경엔 CI 실행 안 함

---

## 최종 ci.yml 흐름

```
PR 열기
    ↓
코드 체크아웃
    ↓
Python 설치
    ↓
패키지 설치 (학습용 + 서빙용)
    ↓
데이터 다운로드
    ↓
모델 학습 (pkl 생성)
    ↓
outputs 폴더 생성
    ↓
pkl 복사
    ↓
pytest 실행 → 9 passed ✅
```

## 회고

> "GitHub Actions CI 구축 중 .gitignore로 제외된 데이터/모델 파일 문제를 겪었고,
> CI 환경에서 데이터 다운로드 → 모델 학습 → 테스트 전체 파이프라인을 자동화해서 해결했습니다"

> 환경 구축의 암묵지를 명시적 자동화로 전환하기"
> 불변의 인프라(Immutable Infrastructure) 관점에서 생각하기
> 로컬 환경의 편의성에 의존하지 않기
