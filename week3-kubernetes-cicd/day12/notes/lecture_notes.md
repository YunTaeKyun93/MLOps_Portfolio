# Day 12 강의 노트 - Orchestrator + Kubernetes

**강의**: [P] Part2 Ch3-07~08
**날짜**: 2026.02.23

---

## 핵심 개념

### Orchestrator란?

여러 컨테이너를 자동으로 배포, 확장, 복구하는 시스템

Docker만 쓰면:

- 컨테이너 죽으면 직접 재시작
- 트래픽 증가 → 수동 스케일
- 여러 서버 관리 불가

Kubernetes는:

- 자동 복구
- 자동 스케일
- 롤링 업데이트 (무중단 배포)
- 로드밸런싱

### 선언형 관리 (가장 중요)

|      | Docker             | Kubernetes         |
| ---- | ------------------ | ------------------ |
| 방식 | 명령형 (직접 실행) | 선언형 (상태 정의) |
| 예시 | `docker run`       | `replicas: 3`      |

```yaml
replicas: 3 # "3개 유지해라"
# 누가 죽이면 → 다시 만들어서 3 유지
# 이걸 Reconciliation Loop라고 함
```

백엔드 비유:

- Docker = 서버에 직접 SSH 접속해서 프로세스 실행
- K8s = "이 상태로 유지해줘" 선언하면 알아서 맞춰줌

---

## Kubernetes 구조

### Control Plane (Master)

- API Server: kubectl 명령 받는 곳
- Scheduler: 어떤 Node에 Pod 올릴지 결정
- Controller Manager: 상태 유지 담당
- etcd: 클러스터 상태 저장 DB

### Node (Worker)

- kubelet: Pod 실행 담당
- kube-proxy: 네트워크 담당
- container runtime: 실제 컨테이너 실행

---

## 핵심 오브젝트

### Pod

- 가장 작은 실행 단위
- 컨테이너 그룹
- 일시적 (죽으면 그냥 사라짐)

### Deployment

- Pod 직접 생성 안 함
- ReplicaSet 통해 Pod 개수 유지
- 롤링 업데이트 가능

```
Deployment → ReplicaSet → Pod → Container
```

---

## 실습 커맨드

```bash
kubectl run <name> --image=<image>      # 단일 Pod 생성 (수동)
kubectl create deployment <name>        # 선언형 관리 시작
kubectl get pods                        # Pod 목록
kubectl get deployments                 # Deployment 목록
kubectl describe pod <name>             # 상세 정보
kubectl edit deployment <name>          # desired state 변경
```

---

## 백엔드 연결

ML 서빙에서 K8s가 필요한 이유:

- 모델 서버 여러 개 필요 → ReplicaSet
- 트래픽 증가 대응 → HPA (자동 스케일)
- 장애 자동 복구 → Reconciliation Loop
- 무중단 배포 → Rolling Update

---

## 아직 안 배운 것 (추후 프로젝트에서)

- Service, Ingress
- HPA (자동 스케일)
- Liveness probe
- Resource limit
- Helm
- CI/CD 연동

---

## 3줄 요약

1. Kubernetes는 "명령 실행 도구"가 아니라 "상태 유지 시스템"이다
2. Deployment는 Pod 개수를 항상 유지한다
3. Orchestrator는 ML 모델 운영 안정성을 위해 필요하다
