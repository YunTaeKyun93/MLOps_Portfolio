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

## 💬 오늘 강의 한 줄 요약

> S3는 MLOps의 파일 서버. 모델/데이터를 S3에 올려두면 어떤 서버에서든 같은 파일을 안전하게 가져다 쓸 수 있다.

---

# Day 19 실습 노트 - S3 모델 업로드 + EC2 다운로드

**날짜**: 2026.03.03
**목표**: S3에 모델 저장 → EC2에서 다운로드

---

## 실습 1: S3 버킷 생성 + 모델 업로드

### 목표

- [x] S3 버킷 생성
- [x] pkl 파일 2개 업로드

### 핵심 명령어

```bash
# S3 버킷 목록 확인
aws s3 ls

# pkl 파일 업로드
aws s3 cp week2-serving/day7-cf-recommender/outputs/user_item_matrix.pkl \
    s3://mlops-movie-recommend-models/models/user_item_matrix.pkl

aws s3 cp week2-serving/day7-cf-recommender/outputs/user_similarity.pkl \
    s3://mlops-movie-recommend-models/models/user_similarity.pkl

# 업로드 확인
aws s3 ls s3://mlops-movie-recommend-models/models/
```

### 결과

```
2026-03-03 19:11:57  179104222 user_item_matrix.pkl
2026-03-03 19:12:17  291901714 user_similarity.pkl
```

### S3 URI 구조

```
s3://mlops-movie-recommend-models/models/user_item_matrix.pkl
      ↑                              ↑           ↑
   버킷명                          폴더         파일명
```

---

## 실습 2: EC2에서 S3 다운로드

### 목표

- [x] EC2 접속
- [x] AWS CLI 설치
- [x] S3에서 pkl 파일 다운로드

### AWS CLI 설치 (Ubuntu)

```bash
# apt로 안 되는 경우
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install -y unzip
unzip awscliv2.zip
sudo ./aws/install

# 확인
aws --version
```

### 자격증명 설정

```bash
aws configure
# AWS Access Key ID:
# AWS Secret Access Key:
# Default region name: ap-northeast-2
# Default output format: json
```

### S3 다운로드

```bash
mkdir -p outputs
aws s3 cp s3://mlops-movie-recommend-models/models/user_item_matrix.pkl outputs/
aws s3 cp s3://mlops-movie-recommend-models/models/user_similarity.pkl outputs/

# 확인
ls outputs/
```

### 결과

```
user_item_matrix.pkl  user_similarity.pkl ✅
```

---

## 🔥 트러블슈팅

| 에러                                             | 원인                             | 해결                       |
| ------------------------------------------------ | -------------------------------- | -------------------------- |
| `Package 'awscli' has no installation candidate` | Ubuntu 24.04에서 apt로 설치 불가 | curl로 awscli v2 직접 설치 |

---

## ✅ 오늘 완성한 것

- [x] S3 버킷 생성 (mlops-movie-recommend-models)
- [x] pkl 파일 2개 S3 업로드
- [x] EC2에서 S3 다운로드 성공

---

## 💡 실무 활용 패턴

```python
# FastAPI 서버 시작 시 S3에서 모델 자동 다운로드
import boto3

def load_model_from_s3():
    s3 = boto3.client('s3')
    s3.download_file(
        'mlops-movie-recommend-models',
        'models/user_item_matrix.pkl',
        'outputs/user_item_matrix.pkl'
    )
```

나중에 ECS 배포할 때 서버 시작 시 자동으로 S3에서 모델 받아오는 구조로 만들 수 있음.

---

## 📝 회고

- **배운 것**: S3 = MLOps 파일 서버. Git에 못 올리는 모델/데이터 저장 용도
- **인상 깊었던 것**: EC2에서 S3 접근할 때 IAM 키 필요. 실무에서는 IAM Role로 더 안전하게
- **내일 연결**: GitHub Actions → ECR 자동 푸시 → ECS 자동 배포 CI/CD 완성

---
