# Day 19 실습 노트 3 - 트러블슈팅 모음

**날짜**: 2026.03.04

---

## 트러블슈팅 목록

| #   | 에러                                    | 원인                                         | 해결                                        |
| --- | --------------------------------------- | -------------------------------------------- | ------------------------------------------- |
| 1   | `platform linux/amd64 does not match`   | M1 Mac ARM 이미지를 amd64 ECS에서 실행 불가  | `docker build --platform linux/amd64`       |
| 2   | `tag is immutable`                      | ECR Immutable tag 설정                       | ECR → 편집 → Mutable로 변경                 |
| 3   | `invalid reference format`              | `$GIT_SHA` 변수가 비어있음 (한 줄 실행 문제) | 명령어 분리해서 실행                        |
| 4   | `TaskDefinition is inactive`            | 기존 Task Definition 삭제로 inactive 상태    | 새 Task Definition 생성                     |
| 5   | `CloudFormation stack already exists`   | 이전 실패한 서비스의 스택 충돌               | CloudFormation 스택 삭제 후 재생성          |
| 6   | `EssentialContainerExited` (종료코드 1) | Dockerfile CMD가 `src.service:app` (구 경로) | `main:app`으로 수정                         |
| 7   | `Could not import module "main"`        | Dockerfile에 `main.py` COPY 누락             | `COPY main.py .` 추가                       |
| 8   | `FileNotFoundError: outputs/pkl`        | CI에서 `best_acc.txt` 읽어서 학습 스킵       | CI에서 `rm -f outputs/best_acc.txt` 후 학습 |
| 9   | `BASE_DIR` 경로 오류                    | `dirname` 횟수 계산 실수                     | `app/services/`에서 3번 올라가야 루트       |
| 10  | `AWS signature mismatch`                | GitHub Secrets에 잘못된 키 저장              | IAM 키 재발급 + Secrets 재설정              |
| 11  | `Merging is blocked`                    | CI job 이름 변경 → Status check 불일치       | job 이름 `test`로 통일                      |
| 12  | API 무한 스피너                         | 보안 그룹 8000 포트 미개방                   | 인바운드 규칙 8000 포트 추가                |

---

## 상세 트러블슈팅

### 1. M1 플랫폼 이슈

```
에러: CannotPullContainerError: image Manifest does not contain descriptor
      matching platform 'linux/amd64'

원인: Mac M1/M2(ARM64)로 빌드한 이미지는 linux/amd64 ECS에서 실행 불가

해결:
docker build --platform linux/amd64 -t movie-recommend .

참고: GitHub Actions는 linux/amd64 환경이라 CI에서 빌드하면 이 문제 없음
```

### 2. ECR Immutable Tag

```
에러: The image tag 'latest' already exists and cannot be overwritten
      because the tag is immutable.

원인: ECR 레포 생성 시 Immutable tag로 설정됨

해결: ECR → movie-recommend → 편집 → Image tag mutability → Mutable
```

### 3. Dockerfile CMD 경로 오류

```
에러: ERROR: Error loading ASGI app. Could not import module "src.service"

원인: Dockerfile CMD가 리팩토링 전 경로 참조
      CMD ["uvicorn", "src.service:app", ...]  ← 구 경로

해결: CMD ["uvicorn", "main:app", ...]  ← 수정
```

### 4. main.py COPY 누락

```
에러: ERROR: Error loading ASGI app. Could not import module "main"

원인: Dockerfile에 main.py 복사 누락
      COPY src/ ./src/   ← main.py는 루트에 있음

해결: COPY main.py . 추가
      COPY app/ ./app/  추가
```

### 5. best_acc.txt CI 이슈

```
에러: ⏭️ 기존 모델 유지 (best: 0.3817 >= 현재: 0.3817)
      → pkl 파일 생성 안 됨 → 테스트 FileNotFoundError

원인: best_acc.txt가 git에 커밋되어 있어서
      CI 환경에서도 기존 성능과 비교 후 저장 스킵

해결: CI 모델 학습 전 best_acc.txt 삭제
      run: |
        rm -f outputs/best_acc.txt
        python src/train.py
```

### 6. GitHub Actions Status Check 불일치

```
에러: Merging is blocked due to pending merge requirements

원인: Branch Protection에 "test" Status check 필수 설정
      근데 ci.yml job 이름을 "test-and-deploy"로 변경함
      → "test" 체크가 영원히 pending

해결: ci.yml job 이름을 다시 "test"로 변경
     jobs:
       test:  ← "test-and-deploy"에서 수정
```

---

## 핵심 교훈

1. **M1 Mac에서 AWS 배포할 때는 항상 `--platform linux/amd64`**
2. **ECR은 처음부터 Mutable로 만들거나, sha 태그만 사용**
3. **Dockerfile 수정 후 반드시 로컬에서 `docker run` 테스트 먼저**
4. **CI job 이름 = Branch Protection Status check 이름 (정확히 일치)**
5. **IAM Secret Key는 생성 시 바로 저장 (나중에 다시 못 봄)**
