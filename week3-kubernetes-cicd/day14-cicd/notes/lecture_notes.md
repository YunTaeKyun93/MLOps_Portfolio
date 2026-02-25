# Day 15 강의 노트 - CI/CD 이론

**강의**: [P] Part2 Ch3-11~12
**날짜**: 2026.02.25

---

## CI/CD란?

**CI (Continuous Integration)**

- 코드 push → 자동 빌드 + 자동 테스트
- "코드 푸시하면 자동으로 검증"

**CD (Continuous Deployment)**

- 테스트 통과 → 자동 프로덕션 배포
- "검증 끝나면 자동으로 서비스 반영"

백엔드 비유:

```
수동: 코드 작성 → docker build → docker push → kubectl apply (사람이 직접)
CI/CD: git push 하나로 위 과정 전부 자동화
```

---

## MLOps에서 CI/CD가 중요한 이유

일반 DevOps CI/CD와 다른 점:

```
일반: 코드 변경 → 빌드 → 배포
MLOps: 코드 변경 + 모델 변경 + 데이터 변경 → 빌드 → 테스트 → 배포 → 모니터링
```

- 모델 반복 속도 향상
- 자동 평가 (성능 기준 미달 시 배포 차단)
- 성능 저하 시 재학습 트리거

---

## CI/CD vs Workflow Management

| 구분      | CI/CD                   | Workflow               |
| --------- | ----------------------- | ---------------------- |
| 목적      | 코드 빌드/테스트/배포   | 데이터 파이프라인 실행 |
| 대상      | 개발자                  | 데이터 엔지니어        |
| 대표 도구 | Jenkins, GitHub Actions | Airflow, Kubeflow      |

- CI/CD → 코드 중심
- Airflow → 데이터 중심

---

## Jenkins vs GitHub Actions

|      | Jenkins        | GitHub Actions  |
| ---- | -------------- | --------------- |
| 서버 | 직접 운영 필요 | GitHub에서 실행 |
| 무게 | 무거움         | 가벼움          |
| 실무 | 대기업 레거시  | 스타트업 표준   |

→ 취업 목표 기준 **GitHub Actions** 선택

---

## CI/CD 자동화 흐름

```
git push
    ↓
GitHub Actions 트리거
    ↓
pytest 자동 실행
    ↓
docker build (멀티 플랫폼)
    ↓
docker push (Docker Hub)
    ↓
kubectl apply (K8s 배포)
```

---

## 3줄 요약

1. CI/CD는 git push 하나로 테스트 → 빌드 → 배포를 자동화한다
2. MLOps CI/CD는 모델 라이프사이클까지 자동화한다
3. 실무에서는 Jenkins보다 GitHub Actions를 많이 쓴다
