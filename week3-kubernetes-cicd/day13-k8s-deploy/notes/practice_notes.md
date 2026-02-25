# Day 13 Practice - Kubernetes Deployment Deep Dive

## 🎯 학습 목적

- Deployment / ReplicaSet / Pod 관계를 내부 동작 기준으로 이해
- Rolling Update, Revision, Rollback 실험을 통해 구조 검증
- Declarative vs Imperative 차이 체감

---

## 1. Kubernetes 기본 구조

```
Deployment
    ↓
ReplicaSet
    ↓
Pod
```

- Deployment는 Pod을 직접 관리하지 않는다
- ReplicaSet이 Pod 개수를 유지한다
- Deployment는 ReplicaSet을 교체하는 상위 컨트롤러다

---

## 2. spec.template이 핵심

```yaml
spec:
  template:
    metadata:
      labels:
        app: ml-api
    spec:
      containers:
        - name: ml-api
          image: ml-api:0.3
```

이 template이 바뀌면:

- 새로운 ReplicaSet 생성
- revision 증가
- Rolling Update 시작

---

## 3. ReplicaSet의 역할

원하는 개수만큼 Pod을 항상 유지하는 컨트롤러

```
현재 4개 → 1개 생성
현재 6개 → 1개 삭제
```

Self-healing의 핵심.

---

## 4. Rolling Update 내부 동작

```bash
kubectl set image deployment/ml-api ml-api=ml-api:0.4 -n ml-project
```

내부에서 벌어지는 일:

1. Deployment spec.template 변경
2. 새로운 ReplicaSet 생성
3. 새 RS scale up
4. 기존 RS scale down
5. revision 증가

> Deployment는 Pod을 교체하는 게 아니라 ReplicaSet을 교체한다.

---

## 5. Revision 개념

```bash
kubectl rollout history deployment/ml-api -n ml-project
```

| Revision | Image      |
| -------- | ---------- |
| 2        | ml-api:0.4 |
| 3        | ml-api:0.3 |

Rollback이 가능한 이유:
이전 ReplicaSet이 삭제되지 않고 `replicas=0` 상태로 남아 있기 때문

---

## 6. Rollback

```bash
kubectl rollout undo deployment/ml-api -n ml-project
```

동작:

- template을 이전 revision으로 변경
- 새로운 revision 생성
- 이전 RS scale down
- 되돌릴 RS scale up

> Rollback은 RS 재사용이 아니라 template을 되돌리는 것

---

## 7. Declarative vs Imperative

**Imperative (명령형)**

```bash
kubectl set image ...
```

- 클러스터 상태 직접 수정
- 빠른 테스트용
- 로컬 YAML은 변경되지 않음

**Declarative (선언형)**

```bash
kubectl apply -f deployment.yaml
```

- 파일을 Source of Truth로 사용
- 실무에서 권장 방식

**실제 경험:**
`set image`로 0.4 변경 후 deployment.yaml이 0.3이어서 apply 시 다시 0.3으로 되돌아감
→ 파일과 클러스터 상태는 반드시 동기화되어야 한다

---

## 8. Namespace

동일 이름 리소스라도 namespace가 다르면 완전히 다른 객체

```
default/ml-api
ml-project/ml-api  ← 완전히 다른 리소스
```

항상 `-n` 옵션 명시 필수

---

## 9. 오늘의 핵심 정리

- Deployment는 Pod을 직접 관리하지 않는다
- ReplicaSet이 Pod 개수를 유지한다
- spec.template이 바뀌면 새 ReplicaSet이 생성된다
- revision은 template 변경 이력이다
- 이전 ReplicaSet은 rollback을 위해 남아 있다
- YAML 파일은 Source of Truth다

---

## 🎤 면접 한 줄 정리

> Deployment는 Pod을 직접 교체하는 리소스가 아니라,
> ReplicaSet을 교체하면서 무중단 배포를 구현하는 상위 컨트롤러입니다.
