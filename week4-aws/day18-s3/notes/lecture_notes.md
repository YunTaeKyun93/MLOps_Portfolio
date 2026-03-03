# Day 18 강의 + 실습 노트 - AWS S3 모델 저장소

**강의**: [P] Part3 Ch3-01~03
**날짜**: 2026.03.03

---

## 오늘 들은 강의

✅ Part3 Ch3-01. SageMaker를 활용한 MLOps 소개 (17:34)
✅ Part3 Ch3-02. SageMaker 계정 생성 및 Free Tier (18:42)
✅ Part3 Ch3-03. 데이터 준비 (일부)

---

## 핵심 개념 정리

### S3 (Simple Storage Service)

AWS 파일 저장소. MLOps에서 모델/데이터 저장용으로 핵심.

```
Git에 올리기 어려운 것들:
- 모델 파일 (pkl, pt) → 수백 MB
- 학습 데이터 (csv)  → 수 GB
→ S3에 저장!
```

장점:

```
- EC2, ECS, Lambda 어디서든 다운로드 가능
- 모델 버전 관리 가능 (v1.0, v2.0)
- 팀원 모두 같은 모델 파일 사용
- 비용 거의 무료 (5GB 무료 티어)
```

백엔드 비유:

```
S3 = CDN + 파일 서버
모델 파일 = 정적 에셋
```

---

### SageMaker

ML 전체 라이프사이클을 AWS에서 관리해주는 플랫폼.

```
- 데이터 준비 (S3 연동)
- 모델 학습 (EC2 자동 프로비저닝)
- 모델 배포 (엔드포인트 자동 생성)
- 모니터링
```

MLflow vs SageMaker:

```
MLflow:
- 오픈소스
- 실험 추적 + 모델 레지스트리
- 어디서든 설치 가능
- 배포는 직접 해야 함

SageMaker:
- AWS 관리형
- 학습 + 배포 + 모니터링 전부 포함
- AWS에서만 가능
- 비용 발생
```

백엔드 비유:

```
MLflow    = Git + 직접 관리
SageMaker = GitHub + Vercel 합친 것 (전부 자동)
```

---

### IAM 자격증명

S3 접근 시 필요한 것:

```
로컬 개발  → aws configure (Access Key 직접 입력)
EC2/ECS   → IAM Role 사용 (키 없이 권한 부여) ← 더 안전
```

IAM Role이 더 안전한 이유:

```
Access Key → 코드에 노출될 위험
IAM Role  → AWS 내부에서 자동 인증, 키 노출 없음
```

---

## ✏️ 핵심 질문 5개

### Q1. S3가 MLOps에서 왜 필요한가?

**A**: 모델 파일(pkl)이나 학습 데이터는 수백 MB~GB라 Git에 올리기 어려움. S3에 저장하면 EC2, ECS 어디서든 다운로드 가능하고 모델 버전 관리도 됨.

### Q2. EC2에서 S3 접근할 때 뭐가 필요한가?

**A**: IAM 유저의 Access Key + Secret Access Key. 실무에서는 IAM Role을 써서 키 없이 권한 부여하는 게 더 안전.

### Q3. SageMaker와 MLflow의 차이는?

**A**: MLflow는 오픈소스로 실험 추적/모델 레지스트리 담당, 배포는 직접 해야 함. SageMaker는 AWS 관리형으로 학습/배포/모니터링 전부 자동화. MLflow는 어디서든, SageMaker는 AWS에서만.

### Q4. S3 버킷 생성 시 리전을 맞춰야 하는 이유는?

**A**: EC2/ECS와 같은 리전이어야 전송 비용 없고 속도 빠름. 다른 리전이면 비용 발생.

### Q5. IAM Role과 Access Key 차이는?

**A**: Access Key는 키가 코드/설정에 저장되어 노출 위험. IAM Role은 AWS 리소스에 직접 권한 부여라 키 없이 안전하게 접근 가능.

---

### SageMaker Ground Truth

AWS 레이블링 작업 오케스트레이터.

```
S3 (원본 데이터)
    ↓
Labeling Job 생성
    ↓
Worker Pool에 Task 배포
    ↓
결과 S3 저장
```

레이블링 인력 선택:

```
Amazon Mechanical Turk → 외부 크라우드소싱
Private               → 내부 인력
Marketplace           → 3rd party 업체
```

---

### SageMaker Data Wrangler

코드 없이 EDA + Feature Engineering 수행 가능한 GUI 툴.

내부 동작:

```
GUI 클릭
    ↓
Studio EC2 인스턴스 실행
    ↓
Pandas/Sklearn 코드 자동 생성
    ↓
결과 S3 저장
    ↓
Pipeline으로 Export 가능
```

즉 **GUI 기반 자동 코드 생성기**.

---

### SageMaker 비용 발생 포인트

| 기능             | 과금 여부           |
| ---------------- | ------------------- |
| Domain 생성      | 거의 없음           |
| Ground Truth Job | 작업 시간만큼       |
| Data Wrangler    | EC2 인스턴스 시간당 |
| Training         | 인스턴스 시간당     |
| Endpoint         | 24시간 과금 ⚠️      |

---

### 전체 데이터 준비 파이프라인

```
Raw Data (S3)
    ↓
Ground Truth (Labeling)
    ↓
Data Wrangler (EDA + Feature Engineering)
    ↓
Training
```

---

## 💬 오늘 강의 한 줄 요약

> S3는 MLOps의 파일 서버. SageMaker는 S3 중심으로 Labeling → Feature Engineering → Training → Deployment 전체를 자동화해주는 AWS 관리형 ML 플랫폼이다.
