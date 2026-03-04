# Day 19 실습 노트 2 - GitHub Actions → ECR CI/CD

**날짜**: 2026.03.04
**목표**: GitHub Actions로 테스트 → ECR 자동 푸시 파이프라인 구축

---

## 최종 ci.yml

```yaml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: 코드 체크아웃
        uses: actions/checkout@v3

      - name: Python 설치
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: 패키지 설치
        working-directory: project1-movie-recommend
        run: |
          pip install -r requirements.txt
          pip install pytest httpx

      - name: 데이터 다운로드
        working-directory: project1-movie-recommend
        run: |
          mkdir -p data/ml-1m
          curl -O https://files.grouplens.org/datasets/movielens/ml-1m.zip
          unzip ml-1m.zip -d data/

      - name: 모델 학습
        working-directory: project1-movie-recommend
        run: |
          rm -f outputs/best_acc.txt   # CI에서 항상 새로 학습
          python src/train.py

      - name: 테스트 실행
        working-directory: project1-movie-recommend
        run: pytest test_service.py -v

      - name: AWS 인증
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-2

      - name: ECR 로그인
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Docker 빌드 & ECR 푸시
        uses: docker/build-push-action@v5
        with:
          context: project1-movie-recommend
          platforms: linux/amd64
          push: true
          tags: |
            947632012584.dkr.ecr.ap-northeast-2.amazonaws.com/movie-recommend:${{ github.sha }}
            947632012584.dkr.ecr.ap-northeast-2.amazonaws.com/movie-recommend:latest
```

---

## CI/CD 파이프라인 흐름

```
PR 오픈
    ↓
GitHub Actions 실행
    ├── Python 설치
    ├── 패키지 설치
    ├── MovieLens 데이터 다운로드
    ├── 모델 학습 (best_acc.txt 삭제 후)
    ├── pytest (9 passed)
    ├── AWS 인증 (IAM)
    ├── ECR 로그인
    └── Docker 빌드 (linux/amd64) & ECR 푸시
            ├── {sha} 태그
            └── latest 태그
    ↓
CI 통과 → 머지 가능
```

---

## GitHub Secrets 설정

| Secret 이름             | 설명                 |
| ----------------------- | -------------------- |
| `AWS_ACCESS_KEY_ID`     | IAM 액세스 키 ID     |
| `AWS_SECRET_ACCESS_KEY` | IAM 시크릿 액세스 키 |

**IAM 필요 권한:**

- `AmazonEC2ContainerRegistryFullAccess`

---

## ✅ 완성한 것

- [x] ci.yml ECR 푸시 추가
- [x] GitHub Secrets 설정
- [x] CI 파이프라인 통과
- [x] ECR에 이미지 자동 푸시 확인

---

## 📝 회고

- 배운 것: GitHub Actions에서 AWS 인증, linux/amd64 크로스 빌드
- 막혔던 부분: job 이름 변경 → Status check 불일치, best_acc.txt CI 이슈
- 내일 연결: Airflow ML 파이프라인
