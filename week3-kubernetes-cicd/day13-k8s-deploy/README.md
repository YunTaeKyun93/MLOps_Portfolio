# Day 13 - 영화 추천 API K8s 배포

## 학습 목표

영화 추천 API를 Kubernetes에 배포하고 외부에서 접근 가능하게 구성

---

## 오늘 한 것

- deployment.yaml 작성 + 배포
- service.yaml 작성 + 배포
- 트러블슈팅 (arm64 멀티 플랫폼 빌드)
- curl로 /health 응답 확인

---

## 핵심 개념

### Deployment

Pod를 원하는 개수만큼 유지하는 리소스

```yaml
replicas: 2 # 항상 2개 유지
```

- Pod 죽으면 자동 재생성
- 버전 업데이트 시 Rolling Update

### Service

외부 트래픽을 받아서 Pod로 연결하는 리소스

```yaml
nodePort: 30800 # 외부 진입점
targetPort: 8000 # 실제 Pod 포트
```

- Pod IP가 바뀌어도 Service IP는 고정
- 라벨로 Deployment와 연결

### 트래픽 흐름

```
localhost:30800
    ↓
Service (ClusterIP)
    ↓
Pod1:8000 or Pod2:8000
```

---

## 트러블슈팅

### arm64 이미지 문제

**에러**: `no matching manifest for linux/arm64/v8`

**원인**: Mac M1/M2(arm64)에서 amd64로만 빌드된 이미지 사용

**해결**:

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t yuntaekyun/movie-recommend:v1.1 --push .
```

---

## 실행 결과

```bash
kubectl get pods -n ml-project
# NAME                                 READY   STATUS    RESTARTS   AGE
# movie-recommender-5dc7b6565-chhlw    1/1     Running   0          Xs
# movie-recommender-5dc7b6565-z4m8d    1/1     Running   0          Xs

curl http://localhost:30800/health
# {"status":"OK","model_loaded":true}
```

---

## 파일 구조

```
day13-k8s-deploy/
├── deployment.yaml
├── service.yaml
├── README.md
└── notes.md
    └──practice_notes.md
```
