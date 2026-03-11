# Day 20 실습 노트

**날짜**: 2026.03.05
**목표**: K8s 배포 복습 + GitHub Actions CI/CD K8s 자동 배포 연동 + 기술블로그 #1 작성

---

## 실습 1: minikube 설치 + 클러스터 시작

### 목표

- [x] minikube 설치
- [x] 클러스터 정상 동작 확인

### 핵심 명령어

```bash
# 설치
brew install minikube

# 클러스터 시작 (M1 Mac은 docker driver 사용)
minikube start --driver=docker

# 확인
kubectl get nodes
# NAME       STATUS   ROLES           AGE     VERSION
# minikube   Ready    control-plane   5m50s   v1.35.1
```

### 백엔드 연결

```
minikube  = Docker Desktop (실행 환경 자체를 만들어주는 도구)
kubectl   = Postman (명령을 내리는 도구)

minikube 없이 kubectl만 있으면
→ 서버 없이 Postman만 있는 것과 같음
```

### 실행 결과

```bash
docker ps
# gcr.io/k8s-minikube/kicbase:v0.0.50 컨테이너 1개 실행 중
# → 이 컨테이너가 K8s 클러스터 자체
```

---

## 실습 2: deployment.yaml + service.yaml 작성

### 목표

- [x] deployment.yaml 작성
- [x] service.yaml 작성
- [x] kubectl apply 성공

### 핵심 코드

**k8s/deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: movie-recommend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: movie-recommend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    metadata:
      labels:
        app: movie-recommend
    spec:
      containers:
        - name: movie-recommend
          image: movie-recommend:latest
          imagePullPolicy: Never
          ports:
            - containerPort: 8000
```

**k8s/service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: movie-recommend
spec:
  selector:
    app: movie-recommend
  ports:
    - port: 80
      targetPort: 8000
  type: NodePort
```

### 실행 결과

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

kubectl get pods
# movie-recommend-57459f8967-jmwr5   1/1   Running   0   83s
# movie-recommend-57459f8967-jt9xj   1/1   Running   0   83s

kubectl get services
# movie-recommend   NodePort   10.96.161.241   <none>   80:31772/TCP   3m57s

minikube service movie-recommend --url
# http://127.0.0.1:56797
# → /docs 접근 성공 ✅
```

### 백엔드 연결

```
Deployment  = PM2 ecosystem.config.js (인스턴스 몇 개 띄울지)
Service     = nginx (고정 포트로 받아서 Pod로 라우팅)
replicas: 2 = PM2 instances: 2
RollingUpdate = pm2 reload (무중단 재시작)
selector.matchLabels = nginx upstream 서버 식별자
```

---

## 실습 3: GitHub Actions K8s 자동 배포 연동

### 목표

- [x] KUBE_CONFIG Secret 등록
- [x] ci.yml K8s 배포 step 추가
- [x] PR → CI 통과 → merge

### 핵심 코드

**kubeconfig base64 인코딩**

```bash
kubectl config view --raw --minify --flatten | base64
# → GitHub Secret KUBE_CONFIG 값으로 등록
```

**ci.yml 추가된 step**

```yaml
- name: K8s 배포
  env:
    KUBE_CONFIG: ${{ secrets.KUBE_CONFIG }}
  run: |
    mkdir -p ~/.kube
    echo "$KUBE_CONFIG" | base64 --decode > ~/.kube/config
    curl -LO "https://dl.k8s.io/release/v1.34.1/bin/linux/amd64/kubectl"
    chmod +x kubectl
    sudo mv kubectl /usr/local/bin/
    kubectl set image deployment/movie-recommend \
      movie-recommend={ECR_URI}/movie-recommend:${{ github.sha }} \
      --kubeconfig ~/.kube/config || true
```

### 백엔드 연결

```
KUBE_CONFIG Secret  = .env 파일을 GitHub Secret에 넣는 것과 동일
base64 decode       = Secret 값 복원
kubectl set image   = 새 버전 이미지로 롤링 업데이트 트리거
|| true             = 연결 실패해도 파이프라인 fail 안 되게
```

---

## 🔥 트러블슈팅

| 에러                               | 원인                                              | 해결                                             |
| ---------------------------------- | ------------------------------------------------- | ------------------------------------------------ |
| `unknown field "spec.matchLabels"` | deployment.yaml에서 `template.spec` 들여쓰기 오류 | `spec`을 `template` 안으로 들여쓰기              |
| `ErrImagePull`                     | minikube가 로컬 Docker 이미지 접근 불가           | `minikube image load` + `imagePullPolicy: Never` |
| kubeconfig 파일 경로 문제          | `--raw` 옵션만으로는 인증서가 파일 경로로 남음    | `--flatten` 옵션 추가                            |

---

## ✅ 오늘 완성한 것

- [x] k8s/deployment.yaml
- [x] k8s/service.yaml
- [x] .github/workflows/ci.yml (K8s 배포 step 추가)
- [x] 기술블로그 #1 초안 (blog1_fastapi_k8s_cicd.md)

---

## 📝 회고

- 배운 것: kubectl vs minikube 차이, Service가 왜 필요한지, YAML 들여쓰기가 구조를 결정한다는 것
- 막혔던 부분: deployment.yaml 들여쓰기 오류, minikube 로컬 이미지 로드
- 내일: Day 21 휴식 🌴 / Day 22부터 Week 4 AWS 클라우드 배포

---

## Git 커밋

```bash
git checkout -b feat/k8s-auto-deploy
git add k8s/ .github/workflows/ci.yml
git commit -m "feat: K8s deployment/service yaml 추가 및 CI/CD 자동 배포 연동"
git push origin feat/k8s-auto-deploy
# → PR 오픈 → CI 통과 → merge ✅
```
