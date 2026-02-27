# Day 15 실습 노트 - GitHub Actions CD + Docker Hub 자동 푸시

**날짜**: 2026.02.26
**목표**: CI/CD 파이프라인에 Docker Hub 자동 빌드 & 푸시 추가

---

## 실습 1: GitHub Secrets 설정

### 목표

- [ ] Docker Hub Access Token 발급
- [ ] GitHub Secrets에 DOCKERHUB_USERNAME 등록
- [ ] GitHub Secrets에 DOCKERHUB_TOKEN 등록

### 순서

1. Docker Hub → Account Settings → Security → New Access Token
   - Description: `mlops-portfolio`
   - Permissions: `Read & Write`
   - 토큰 복사 (한 번만 보여줌!)

2. GitHub repo → Settings → Secrets and variables → Actions → New repository secret
   - `DOCKERHUB_USERNAME` = `yuntaekyun`
   - `DOCKERHUB_TOKEN` = `dckr_pat_...`

### 핵심 코드

```yaml
- name: Docker Hub 로그인
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

### 백엔드 연결

```
.env 파일에 DB_PASSWORD 넣는 것 = GitHub Secrets에 토큰 넣는 것
process.env.DB_PASSWORD = ${{ secrets.DOCKERHUB_TOKEN }}
```

---

## 실습 2: ci.yml Docker Hub 푸시 추가

### 목표

- [ ] docker/login-action step 추가
- [ ] docker/build-push-action step 추가
- [ ] Version Pinning 적용 (commit sha 태그)

### 핵심 코드

```yaml
- name: Docker Hub 로그인
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}

- name: Docker 빌드 & 푸시
  uses: docker/build-push-action@v5
  with:
    context: week2-serving/day8-fastapi
    push: true
    tags: yuntaekyun/movie-recommend:${{ github.sha }}
```

### `uses` vs `run` 정리

```yaml
uses: docker/login-action@v3 # 남이 만든 액션 가져다 쓰기 (npm install 같은 느낌)
run: pytest test_service.py # 직접 터미널 명령어 실행
```

### Version Pinning

```
${{ github.sha }} = 현재 커밋의 고유 해시값
예: 3e3d3bdb0dac8e65b4179b6701e3685f99a440e5

→ Docker Hub에 이렇게 저장됨:
yuntaekyun/movie-recommend:3e3d3bdb0dac8e65b4179b6701e3685f99a440e5
```

---

## 실습 3: Branch Protection + Required Status Checks

### 목표

- [ ] PR 템플릿 적용 확인
- [ ] CI 통과해야만 머지 가능하도록 설정
- [ ] `CI / test (pull_request)` Required 체크 등록

### 순서

1. Settings → Branches → main-protection
2. `Require status checks to pass` 체크
3. `Add checks` → `test` 검색 → `test GitHub Actions` 선택
4. `Require branches to be up to date before merging` 체크
5. 저장

### 결과

```
PR 열기
    ↓
CI 자동 실행
    ↓
실패 → 머지 불가 ❌
성공 → 머지 가능 ✅
```

---

## 최종 ci.yml 전체 구조

```yaml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      # 1. 코드 가져오기
      - name: 코드 체크아웃
        uses: actions/checkout@v3

      # 2. Python 환경 설정
      - name: Python 설치
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      # 3. 패키지 설치
      - name: 패키지 설치
        run: |
          pip install -r week2-serving/day7-cf-recommender/requirements.txt
          pip install -r week2-serving/day8-fastapi/requirements.txt
          pip install pytest httpx

      # 4. 데이터 준비
      - name: 데이터 다운로드
        working-directory: week2-serving/day7-cf-recommender
        run: |
          mkdir -p data/ml-1m
          curl -O https://files.grouplens.org/datasets/movielens/ml-1m.zip
          unzip ml-1m.zip -d data/

      # 5. 모델 학습
      - name: 모델 학습
        working-directory: week2-serving/day7-cf-recommender
        run: python src/train.py

      # 6. 파일 준비
      - name: outputs 폴더 생성
        run: mkdir -p week2-serving/day8-fastapi/outputs

      - name: pkl 복사
        run: cp week2-serving/day7-cf-recommender/outputs/*.pkl week2-serving/day8-fastapi/outputs/

      # 7. 테스트 실행
      - name: 테스트 실행
        working-directory: week2-serving/day8-fastapi
        run: pytest test_service.py -v

      # 8. Docker Hub 배포
      - name: Docker Hub 로그인
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Docker 빌드 & 푸시
        uses: docker/build-push-action@v5
        with:
          context: week2-serving/day8-fastapi
          push: true
          tags: yuntaekyun/movie-recommend:${{ github.sha }}
```

---

## 🔥 트러블슈팅

| 에러                                           | 원인                                      | 해결                                                |
| ---------------------------------------------- | ----------------------------------------- | --------------------------------------------------- |
| `unauthorized: incorrect username or password` | ci.yml username/password에 콜론(`:`) 오타 | `username: :${{...}}` → `username: ${{...}}`        |
| Secrets 등록 오류                              | 두 개를 하나의 Secret에 같이 넣음         | DOCKERHUB_USERNAME / DOCKERHUB_TOKEN 각각 따로 등록 |
| CI pending 상태 지속                           | Branch Protection에 잘못된 체크 이름 등록 | 삭제 후 `test GitHub Actions` 로 재등록             |

---

## ✅ 오늘 완성한 것

- [x] .github/workflows/ci.yml 완성
- [x] Docker Hub 자동 푸시 확인
  - `yuntaekyun/movie-recommend:3e3d3bdb...`
- [x] Branch Protection + Required Status Checks 설정
- [x] PR 템플릿 적용 확인

---

## 📝 회고

- **배운 것**: Version Pinning 개념. 커밋 sha = 이미지 태그로 배포 추적 가능
- **막혔던 부분**: 콜론 오타 하나 때문에 Docker Hub 로그인 계속 실패. 에러 메시지만 보고 토큰 문제인 줄 알았는데 ci.yml 코드 문제였음
- **내일 연결**: AWS ECS 배포 (Week 4)

---

## 📊 완성된 CI/CD 파이프라인 흐름

```
개발자
    ↓
git push (브랜치)
    ↓
PR 생성
    ↓
GitHub Actions 자동 실행
    ├── 데이터 다운로드
    ├── 모델 학습
    ├── pytest (9 passed ✅)
    ├── Docker 빌드
    └── Docker Hub 푸시
    ↓
CI 통과 → 머지 가능
    ↓
main 브랜치 머지
```

---

## Git 커밋

```bash
git add .
git commit -m "feat: CI에 Docker Hub 자동 푸시 추가"
git push origin feat/day16-docker-hub-push
```
