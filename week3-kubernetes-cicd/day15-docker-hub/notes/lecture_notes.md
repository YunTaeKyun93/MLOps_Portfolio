# Day 16 강의 노트 - CI/CD와 테스팅

**강의**: [B] Part4 Ch4-01~03
**날짜**: 2026.02.26

---

## 오늘 들은 강의

✅ 01. Continuous Deployment (CD) 소개 (38:28)
✅ 02. 테스팅 (29:24)
✅ 03. Continuous Integration (CI) 소개 (1:01:37)

---

## 01. Continuous Deployment (CD) 소개

### 핵심 개념

CD = 코드 변경이 발생하면 자동으로 배포 프로세스를 실행하는 것

```
모델 코드 작성
    ↓
패키징 → 평가 → 배포
    ↓
태깅 → 리포트
```

### MLOps에서 CD 위치

```
Verify → Package → Release
  ↑          ↑         ↑
테스트    Docker빌드   실제배포
```

### 실제 CD 파이프라인 구조

```
User → GitHub → GitHub Actions
                    ↓
              Docker Build
                    ↓
              Registry Push
                    ↓
              배포 실행
```

강의 예시는 GCP(Vertex AI) 기준이지만 개념은 동일:

```
강의: GitHub Actions → Docker → GCR → Vertex AI
우리: GitHub Actions → Docker → Docker Hub → K8s
```

### GitHub Actions Secret 설정

코드에 토큰/키를 직접 쓰면 보안 사고 발생.

```yaml
# 잘못된 방법 (절대 하면 안 됨)
password: dckr_pat_xxxxx

# 올바른 방법
password: ${{ secrets.DOCKERHUB_TOKEN }}
```

GitHub → Settings → Secrets에 등록 후 `${{ secrets.이름 }}` 으로 참조.

### Version Pinning 전략

```yaml
tags: yuntaekyun/movie-recommend:${{ github.sha }}
```

```
커밋 sha = Docker 이미지 태그
3e3d3bdb... = yuntaekyun/movie-recommend:3e3d3bdb...
```

장점:

- 어떤 커밋에서 어떤 이미지가 만들어졌는지 추적 가능
- 롤백 시 이전 sha 태그로 바로 되돌릴 수 있음
- 배포 이력 관리 가능

### 백엔드 연결

```
NestJS 배포 (수동): 서버 접속 → git pull → npm install → pm2 restart
CD (자동):          git push → 자동으로 위 과정 전부 실행
```

### 💡 인상 깊었던 것

- Version Pinning: 커밋 sha = 이미지 태그라는 개념이 배포 추적에 매우 강력함
- Secret 관리: 코드에 직접 토큰 쓰는 게 얼마나 위험한지 다시 상기됨

---

## 02. 테스팅

### 핵심 개념

테스트 없이 배포하면:

```
Function A 수정
    ↓
Function B, C가 깨질 수 있음
    ↓
사람이 일일이 확인해야 함 → 불가능
```

해결책: 자동화된 테스트

### pytest

파이썬 표준 테스트 프레임워크

```python
# given / when / then 패턴
def test_recommend():
    # given (준비)
    user_id = 1

    # when (실행)
    result = recommend(user_id)

    # then (검증)
    assert len(result) > 0
```

### parametrize - 여러 케이스 한번에 테스트

```python
@pytest.mark.parametrize(
    "given, expected",
    [
        ((1, 3), 4),
        ((2, 7), 9),
        ((-1, 4), 3),
    ]
)
def test_add(given, expected):
    result = add(*given)
    assert result == expected
```

### 테스트 종류

| 종류             | 범위                 | 속도 |
| ---------------- | -------------------- | ---- |
| Unit Test        | 개별 함수            | 빠름 |
| Integration Test | 여러 모듈 연결       | 보통 |
| E2E Test         | 사용자 시나리오 전체 | 느림 |

실무 비율:

```
Unit Test       70%
Integration     20%
E2E             10%
```

### pytest-cov - 테스트 커버리지

```bash
pip install pytest-cov
pytest --cov .
pytest --cov --cov-report html tests/
```

```
Total 867 lines
421 lines covered
= 48.5% coverage
```

커버리지 = 테스트가 실행된 코드 비율. 높을수록 안전.

### 나중에 추가할 것

- `fixture`: 테스트 공통 설정 분리
- `mock`: 외부 의존성 (DB, API) 가짜로 대체
- `given/when/then`: 테스트 코드 패턴

### 백엔드 연결

```
NestJS에서 Jest로 테스트하는 것과 동일한 개념
Jest      = pytest
describe  = 테스트 클래스
it/test   = def test_xxx
expect    = assert
```

---

## 03. Continuous Integration (CI) 소개

### 핵심 개념

CI = 코드가 변경될 때마다 자동으로 품질 검증을 수행하는 것

```
코드 수정
    ↓
Linting → Formatting → Type Check → Testing → Coverage
    ↓
통과하면 Merge 허용 / 실패하면 Merge 차단
```

### CI가 필요한 이유

1. **코드 신뢰성 증대**: 변경 즉시 테스트 → 버그 조기 발견
2. **조직 컨벤션 유지**: 포맷/스타일 강제 → 팀 전체 일관성
3. **반복 작업 자동화**: Lint/Test 수동 실행 제거
4. **형상 가시성 확보**: Coverage, 품질 지표 확보

### CI 구성 요소

| 영역       | 도구                 |
| ---------- | -------------------- |
| 코드 품질  | Black, isort, flake8 |
| 타입 검사  | mypy                 |
| 테스트     | pytest               |
| 커버리지   | pytest-cov           |
| Pre-commit | pre-commit           |

### Black - 코드 자동 포맷팅

```bash
pip install black
black --check .
```

팀 스타일 통일용. 자동으로 코드 정렬해줌.

### mypy - 타입 검사

```python
# 타입 없음 → mypy 검사 불가
def add(a, b):
    return a + b

# 타입 있음 → mypy가 정적 분석 가능
def add(a: int, b: int) -> int:
    return a + b
```

```bash
pip install mypy
mypy .
```

### Quality Gate

```yaml
# 커버리지 70% 미만이면 CI 실패
pytest --cov=. --cov-report=term-missing --cov-fail-under=70
```

이게 진짜 품질 방어선.

### Pre-commit - 로컬 1차 방어

```bash
pip install pre-commit
pre-commit install
```

`.pre-commit-config.yaml` 에 설정:

- trailing whitespace 제거
- black 자동 실행
- mypy 검사
- isort 정렬
- pytest 실행

```
commit 버튼 누르기 전에 자동 검사
→ CI에 올라가기 전에 로컬에서 먼저 잡아냄
```

### CI vs CD 완전 정리

| 구분      | CI               | CD                   |
| --------- | ---------------- | -------------------- |
| 목적      | 코드 품질 보장   | 자동 배포            |
| 실행 시점 | Commit / PR      | CI 통과 후           |
| 주요 작업 | Lint, Type, Test | Docker Build, Deploy |
| 실패 시   | Merge 차단       | 배포 차단            |

### 백엔드 연결

```
ESLint      = Black (코드 포맷터)
TypeScript  = mypy (타입 검사)
Jest        = pytest (테스트)
Husky       = pre-commit (로컬 훅)
```

NestJS 개발할 때 쓰던 것들과 1:1 대응됨.

---

## ✏️ 핵심 질문 5개

### Q1. CI와 CD의 차이는?

**A**: CI는 코드 품질 자동화 (Merge 차단), CD는 배포 자동화 (Deploy 자동 실행). CI가 통과해야 CD가 실행됨.

### Q2. Version Pinning이 왜 중요한가?

**A**: 커밋 sha를 이미지 태그로 쓰면 어떤 코드에서 어떤 이미지가 만들어졌는지 추적 가능. 장애 발생 시 이전 sha 태그로 즉시 롤백 가능.

### Q3. GitHub Secrets가 필요한 이유는?

**A**: 토큰/키를 코드에 직접 쓰면 GitHub에 노출되어 보안 사고 발생. Secrets에 등록하면 암호화되어 저장되고 Actions 실행 시에만 주입됨.

### Q4. pytest-cov의 `--cov-fail-under=70`은 무엇인가?

**A**: 테스트 커버리지가 70% 미만이면 CI를 실패시키는 Quality Gate. 코드 품질 기준선을 강제하는 것.

### Q5. pre-commit과 CI의 차이는?

**A**: pre-commit은 로컬에서 commit 전에 검사 (1차 방어), CI는 GitHub에서 PR 시 검사 (2차 방어). 두 개를 같이 쓰면 버그가 원격까지 올라가기 전에 잡을 수 있음.

---

## 💬 오늘 강의 한 줄 요약

> CI는 품질 방어선, CD는 배포 자동화. git push 하나로 테스트 → 빌드 → 배포가 자동으로 돌아가는 구조가 진짜 MLOps다.
