# Day 5 실습 노트

**날짜**: 2026.02.13
**실습**: Docker 기초 - Dockerfile 작성 + 실험

---

## 실습 1: 기본 명령어 확인

```bash
docker --version
docker run hello-world
docker images
docker ps -a
```

✅ 완료

---

## 실습 2: Dockerfile 작성 + 빌드 성공

### 최종 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src/
COPY outputs ./outputs/

CMD ["python", "src/predict.py"]
```

### 최종 requirements.txt

```
pandas==2.3.3
numpy==2.4.1
scikit-learn==1.8.0
joblib==1.3.2
```

### 실행 결과

```
모델 로드 완료
모델이 기대하는 컬럼: ['Pclass' 'Age' 'SibSp' 'Parch' 'Fare'
                       'Sex_female' 'Sex_male' 'Embarked_C' 'Embarked_Q' 'Embarked_S']

🎯 예측 결과:
   생존 여부: 생존 ✅
   생존 확률: 99.00%
   사망 확률: 1.00%
```

✅ 컨테이너에서 predict.py 실행 성공!

---

## 트러블슈팅

### 에러 1: numpy.dtype size changed

```
ValueError: numpy.dtype size changed,
may indicate binary incompatibility.
Expected 96 from C header, got 88 from PyObject
```

**원인**:

```
requirements.txt에 numpy 버전 미지정
→ pip이 최신 numpy 설치
→ 모델 저장 당시 numpy 버전과 충돌
```

**해결**:

```
pip freeze | grep -E "pandas|numpy|scikit-learn|joblib"
→ 로컬 버전 확인 후 requirements.txt에 명시적 고정
```

---

### 에러 2: No module named 'numpy.\_core'

```
ModuleNotFoundError: No module named 'numpy._core'
```

**원인**:

```
numpy 2.0+ 에서 내부 구조 변경 (_core 모듈 추가)
로컬: numpy 2.4.1로 모델 저장
컨테이너: 다른 버전 설치 → 로드 실패
```

**해결**:

```
numpy==2.4.1 버전 고정
```

**배운 것**:

```
Docker가 재현성을 보장하는 도구지만
버전 고정을 안 하면 Docker도 소용없음!
requirements.txt = 로컬 환경 스냅샷
→ pip freeze로 버전 뜨는 습관 필수!
```

---

## [VS] 이미지 크기 비교

```bash
docker pull python:3.11
docker pull python:3.11-slim
docker images | grep python
```

### 결과

| 이미지                    | 크기   |
| ------------------------- | ------ |
| python:3.11               | 3.19GB |
| python:3.11-slim          | 212MB  |
| titanic-model (slim 기반) | 711MB  |

```
slim이 full 대비 93% 작음!
titanic-model = slim(212MB) + pandas + numpy + sklearn 설치 = 711MB
```

**면접 답변 재료**:

```
"python:3.11-slim을 선택한 이유:
 1. ML 라이브러리(glibc 의존) 호환 → alpine 불가
 2. full 대비 93% 크기 절감 (3.19GB → 212MB)
 3. ML 서빙 환경 표준"
```

---

## [WHAT IF] COPY 순서 실험

### Dockerfile.bad (비효율)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "src/predict.py"]
```

### 실험 방법

```
src/predict.py 코드 수정 후 각각 재빌드
```

### 결과

| Dockerfile                   | 재빌드 시간 |
| ---------------------------- | ----------- |
| Dockerfile.bad (비효율)      | 33.156초    |
| Dockerfile (효율, 캐시 활용) | 0.467초     |

```
캐시 활용하면 70배 빠름!!

이유:
비효율: 코드 수정 → COPY . . 캐시 깨짐
        → pip install 처음부터 다시 (오래 걸림!)

효율:   코드 수정 → requirements.txt는 그대로
        → pip install 캐시 유지!
        → COPY src/ 만 다시 실행
```

**포트폴리오 수치**:

```
"COPY 순서 최적화로 재빌드 시간 33초 → 0.5초 단축 (70배)"
```

---

## [WHAT IF] .dockerignore 효과

### 결과

| 상태               | 이미지 크기 |
| ------------------ | ----------- |
| .dockerignore 없음 | 711MB       |
| .dockerignore 있음 | 711MB       |

```
차이 없음 → 이유:
제외 대상 파일들이 KB 단위로 작아서 티가 안 남
(notes/, *.md 등)
```

**실무에서 진짜 효과나는 경우**:

```
- data/ 폴더에 GB 단위 학습 데이터
- .git/ 히스토리 (프로젝트 클수록 큼)
- node_modules/ (수백 MB)

→ 습관적으로 .dockerignore 작성하는 게 맞음!
  지금은 작아서 티 안 나는 것
```

---

## [WHY] --no-cache-dir

### 실험 결과

| Dockerfile          | 이미지 크기 |
| ------------------- | ----------- |
| --no-cache-dir 있음 | 711MB       |
| --no-cache-dir 없음 | 853MB       |

```
142MB 차이!
```

### 원인

```
pip install 기본 동작:
1단계: wheel 파일 다운로드
       → /root/.cache/pip/ 에 저장
2단계: wheel로 실제 설치
       → /usr/local/lib/python3.11/site-packages/

→ 설치 끝나도 /root/.cache/pip/ 에 파일 남음!
  이미지 레이어에 포함 → 142MB 낭비
```

**백엔드 비유**:

```
npm install 후 node_modules/.cache가
빌드 이미지에 그대로 포함된 것과 동일

--no-cache-dir = 설치 후 캐시 폴더 안 만들기
```

**결론**:

```
로컬 개발: --no-cache-dir 없어도 됨
           (다음 설치 때 캐시로 빠르게)

Docker 이미지: --no-cache-dir 필수!
               어차피 다시 설치 안 함
               → 캐시 = 그냥 용량 낭비
               → 142MB 절약!
```

---

## 오늘 실험 전체 요약

| 실험           | 결과                        | 포트폴리오 재료 |
| -------------- | --------------------------- | --------------- |
| slim vs full   | 212MB vs 3.19GB (93% 절감)  | ✅              |
| COPY 순서      | 0.5초 vs 33초 (70배 차이)   | ✅              |
| .dockerignore  | 차이 없음 (파일 작아서)     | 실무 이해 ✅    |
| --no-cache-dir | 711MB vs 853MB (142MB 절감) | ✅              |

---

## Week 9 개선 예정

```
docker dive 적용:
→ 레이어별 크기 분석
→ 불필요한 파일 추가 제거

Multi-stage build:
→ builder stage + runtime stage
→ 더 작은 최종 이미지 목표
→ 현재 711MB → 목표 400MB 이하
```

---

**Status**: 완료 ✅
**Next**: Day 6 - FastAPI 기초 (오늘 Docker 이미지 위에서 서빙!)
