# Day 18 강의 노트 - AWS ECS + ECR 배포

**강의**: [B] Part2 Ch3-03~04
**날짜**: 2026.03.02

---

## 오늘 들은 강의

✅ 03. FastAPI 컨테이너 배포 1 - AWS ECS 구성하기 (25:08)
✅ 04. FastAPI 컨테이너 배포 2 - AWS ECS 서비스 배포 (15:19)

---

## 핵심 개념 정리

### 전체 흐름

```
Local Docker 이미지
    ↓
ECR (이미지 저장소)
    ↓
Task Definition (실행 설계도)
    ↓
ECS Service (실행 + 유지)
    ↓
Fargate (서버리스 실행)
    ↓
Public IP → 외부 접속
```

---

### ECR (Elastic Container Registry)

AWS 전용 Docker 이미지 저장소.

```
Docker Hub = 공개 이미지 저장소 (누구나 접근)
ECR        = AWS 전용 프라이빗 저장소 (IAM 접근 제어)
```

특징:

- AWS 리전별 서비스
- ECS/Fargate랑 연동 빠름
- 같은 리전이면 전송 비용 없음
- 이미지 저장만 함 (실행은 안 함)

실무 기준:

```
사이드 프로젝트 → Docker Hub (편함)
AWS 배포        → ECR (보안 + 속도)
```

---

### ECS (Elastic Container Service)

AWS 관리형 컨테이너 오케스트레이션.

```
K8s  = 오픈소스 (직접 설치/관리 필요, 어디서든 가능)
ECS  = AWS 관리형 (AWS가 다 관리, AWS에서만 가능)
```

구조:

```
Cluster (실행 공간)
    ↓
Service (Task 유지 + 자동 재시작)
    ↓
Task (실제 실행된 컨테이너 묶음)
    ↓
Container (컨테이너)
```

K8s 비교:
| Kubernetes | ECS |
|------------|-----|
| Deployment | Service |
| Pod | Task |
| Container | Container |
| Docker Hub/ECR | ECR |
| Ingress | ALB |

---

### Task Definition

컨테이너 실행 설계도. K8s의 `deployment.yaml template`과 동일.

포함 내용:

```
- 이미지 (ECR URI)
- CPU / Memory
- Port
- 환경 변수
- 로그 설정 (CloudWatch)
```

---

### Fargate

서버리스 컨테이너 실행 환경.

```
EC2 방식:
- 내가 서버 직접 관리
- OS, Docker 설치 직접
- 커스텀 자유롭지만 관리 부담

Fargate 방식:
- 서버 신경 안 써도 됨
- CPU/메모리만 지정하면 끝
- 관리 편하지만 커스텀 제한
```

백엔드 비유:

```
EC2      = 직접 서버 구축
Fargate  = Vercel/Railway 같은 PaaS
```

---

### 네트워크 설정

ECS Fargate는 `awsvpc` 네트워크 모드 사용.

외부 접속 위해 필요한 것:

```
1. Public IP ENABLED
2. Security Group → 8000번 포트 오픈
3. FastAPI → 0.0.0.0으로 실행
```

---

## ✏️ 핵심 질문 5개

### Q1. ECR과 Docker Hub의 차이는?

**A**: 둘 다 이미지 저장소. Docker Hub는 공개 저장소로 누구나 접근 가능. ECR은 AWS 전용 프라이빗 저장소로 IAM으로 접근 제어하고 ECS와 연동이 빠름.

### Q2. Task Definition이 K8s에서 뭐랑 비슷한가?

**A**: deployment.yaml의 template 부분. 이미지, CPU/메모리, 포트, 환경변수 설정하는 컨테이너 실행 설계도.

### Q3. Fargate와 EC2 방식의 차이는?

**A**: EC2는 서버 직접 관리, Fargate는 서버리스. CPU/메모리만 지정하면 AWS가 알아서 실행해줌. 커스텀은 EC2가 자유롭지만 관리 부담이 있음.

### Q4. ECS Service의 역할은?

**A**: Task를 원하는 개수만큼 유지. 컨테이너 죽으면 자동 재시작. K8s Deployment와 유사.

### Q5. ECS와 K8s 중 실무에서 언제 어떤 걸 쓰나?

**A**: AWS만 쓰면 ECS가 편함 (관리 부담 적음). 멀티 클라우드나 온프레미스도 써야 하면 K8s. 스타트업은 ECS, 대기업은 K8s 많이 씀.

---

## 💬 오늘 강의 한 줄 요약

> ECS는 AWS 버전 K8s. ECR에 이미지 올리고 Task Definition으로 설계도 만들고 Service로 실행하면 Fargate가 서버 없이 컨테이너를 자동으로 관리해준다.
