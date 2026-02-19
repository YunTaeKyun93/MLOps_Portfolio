# Day 9 강의 노트

**강의**: [B] CH5 Clip 1~6 - MLOps 구현을 도와주는 플랫폼들  
**날짜**: 2026.02.19

---

## Ch5-01. MLOps 플랫폼 개요

### 핵심 개념

MLOps를 A to Z 직접 구현하는 것은 매우 복잡하다. 이를 쉽고 편하게 구현할 수 있도록 도와주는 플랫폼들이 존재한다.

**주요 MLOps 플랫폼**

- MLflow - 오픈소스 실험 추적/모델 관리
- Kubeflow - K8s 기반 ML 워크플로우
- Tensorflow Extended (TFX)
- Pytorch Lightning
- Databricks
- Amazon SageMaker - AWS 완전관리형
- Google Cloud AI Platform - GCP 완전관리형

---

## Ch5-02. MLflow

### 핵심 개념

머신러닝 프로젝트를 관리하기 위한 **오픈소스 플랫폼**.  
Project Lifecycle의 모든 단계(개발/학습/추론/배포)에서 사용 가능. 각 컴포넌트는 독립적으로 사용 가능.

### 4가지 핵심 컴포넌트

| 컴포넌트            | 역할                                                                                                                         |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **MLflow Tracking** | 모델 학습 결과 추적. 하이퍼파라미터/손실/성능 지표 기록. Entity Store(경량 메타데이터) + Artifact Store(모델 파일 등 대용량) |
| **MLflow Projects** | 코드/환경 설정/종속성 관리. Conda, Docker로 Dependency 정의. 어느 환경에서든 동일하게 실행                                   |
| **MLflow Models**   | 학습된 모델을 관리하고 다양한 환경에서 배포                                                                                  |
| **MLflow Registry** | 모델 버전을 중앙화된 방식으로 관리. dev → staging → production 스테이지                                                      |

### 백엔드 관점 연결

```
MLflow Tracking  ↔  Git 커밋 히스토리 (실험 이력 추적)
MLflow Projects  ↔  package.json (의존성 명시)
MLflow Registry  ↔  npm registry (버전 관리 저장소)
모델 스테이지     ↔  dev/staging/prod 배포 환경 분리
```

---

## Ch5-03. Kubeflow

### 핵심 개념

**쿠버네티스 기반** ML 워크플로우 관리/배포 오픈소스 플랫폼.  
End-to-End ML 솔루션 제공. K8s와 결합해 확장성/안정성/보안성 확보.

### 5가지 주요 기능

**① Kubeflow Pipelines**

- ML 워크플로우 각 단계를 파이프라인으로 정의/자동화
- 각 단계는 **독립적인 컨테이너**로 실행 → 환경 격리 보장
- 재사용 가능한 컴포넌트, 실험 추적, 스케줄링 지원

**② Kubeflow Serving**

- 훈련된 모델을 프로덕션 환경에 배포
- TF/PyTorch/XGBoost/Scikit-Learn 지원
- A/B 테스팅, 자동 스케일링, REST/gRPC 지원

**③ Katib**

- 자동화된 하이퍼파라미터 튜닝
- 그리드 서치, 랜덤 서치, 베이지안 최적화 등 지원

**④ Metadata Store**

- 실험/모델/데이터셋 메타데이터를 중앙 관리
- ML 프로젝트의 투명성과 재현성 향상

**⑤ Jupyter Notebooks Integration**

- Kubeflow 환경 내에서 Jupyter 노트북 생성/관리
- 클라우드 저장소 연동 가능

### 백엔드 관점 연결

```
Kubeflow Pipelines  ↔  GitHub Actions workflow
Kubeflow Serving    ↔  NestJS 컨트롤러 (API 서빙)
자동 스케일링        ↔  로드밸런서 + 오토스케일링
Katib               ↔  A/B 테스트 자동화
```

---

## Ch5-04. Amazon SageMaker

### 핵심 개념

**AWS 클라우드 기반 완전관리형 ML 플랫폼**.  
빌드/학습/배포 전 과정을 하나의 통합 환경에서 제공.

### 핵심 기능

| 기능                    | 설명                                                                |
| ----------------------- | ------------------------------------------------------------------- |
| **ML 수명주기 자동화**  | 데이터 준비 → 모델 훈련 → 평가 → 배포 전 과정 자동화                |
| **SageMaker Pipelines** | ML Workflow 자동화 파이프라인                                       |
| **CI/CD 지원**          | 코드 변경 자동 감지/통합, 자동 테스트, 원클릭 배포, 지속적 모니터링 |
| **모델 관리 및 추적**   | 모델 버전 관리, 성능 지표 추적, 사용 사례별 최적화                  |
| **SageMaker Studio**    | Jupyter 노트북, 코드 에디터, 시각화 통합 ML 개발 환경               |

### 백엔드 관점 연결

```
SageMaker Pipelines  ↔  CI/CD 파이프라인 (GitHub Actions)
SageMaker Studio     ↔  VSCode + 통합 개발 환경
Model Monitor        ↔  서버 모니터링/알림 시스템
```

---

## Ch5-05. GCP AI Platform

### 핵심 개념

**Google 클라우드 기반 ML 플랫폼**. Vertex AI를 중심으로 구성.

### 4가지 컴포넌트

| 컴포넌트                    | 설명                                               |
| --------------------------- | -------------------------------------------------- |
| **AI Notebooks / Training** | JupyterLab 환경에서 코드 작성 및 실험              |
| **Prediction**              | 훈련된 모델 배포 및 대규모 예측 관리형 서비스      |
| **Pipeline**                | ML 워크플로우 자동화. **Kubeflow Pipeline과 호환** |
| **Explainable AI**          | ML 모델의 예측을 설명하기 위한 기술 제공           |

### 핵심 기능 상세

**CI/CD (Cloud Build)**  
코드 변경 → 자동 통합 → 자동 배포. GitHub Actions와 유사

**Vertex AI & BigQuery**

- Vertex AI: 사용자 관리형 JupyterLab 워크북
- BigQuery: 서버리스 데이터 웨어하우스, 대규모 쿼리/분석

**Feature Store** ⭐  
중앙화된 피처 저장소. **훈련-서빙 스큐(Train-Serving Skew) 방지**가 핵심!  
→ 훈련 때 쓴 피처와 서빙 때 쓰는 피처를 동일하게 유지

**GKE (Google Kubernetes Engine)**  
Kubeflow 파이프라인 호스팅. 자원 관리 및 자동 스케일링

---

## Ch5-06. 정리

### 플랫폼 비교

| 플랫폼              | 특징                         | 주요 용도                     | 비용               |
| ------------------- | ---------------------------- | ----------------------------- | ------------------ |
| **MLflow**          | 오픈소스, 로컬/온프레미스    | 실험 추적, 모델 버전 관리     | 무료               |
| **Kubeflow**        | K8s 기반 오픈소스            | 파이프라인 자동화, 모델 서빙  | 무료 (인프라 비용) |
| **SageMaker**       | AWS 완전관리형               | End-to-End ML, 엔터프라이즈   | 유료               |
| **GCP AI Platform** | Google 완전관리형, Vertex AI | BigQuery 연동, TFX 파이프라인 | 유료               |

### 선택 기준

- 스타트업/개인 프로젝트 → **MLflow** (무료, 간단)
- K8s 인프라가 있다면 → **Kubeflow** (오픈소스, 확장성)
- AWS 사용 중 → **SageMaker** (완전관리형, 러닝커브 낮음)
- GCP 사용 중 → **Vertex AI** (BigQuery 연동이 강력)

---

## ✏️ 핵심 질문 3개

**Q1. MLflow Registry의 스테이지 관리가 NestJS 배포 환경 분리와 어떻게 다른가?**  
→ MLflow는 동일 서버에서 모델 '상태'만 변경. NestJS는 물리적으로 다른 서버에 배포. 하지만 개념은 동일 - 검증 후 프로덕션 승격.

**Q2. Kubeflow Serving이 Day 8에서 만든 FastAPI 서비스와 무엇이 다른가?**  
→ FastAPI는 수동으로 만든 서빙 레이어. Kubeflow Serving은 모델 서빙에 특화된 관리형 플랫폼 - A/B 테스팅, 자동 스케일링, 모니터링이 기본 제공됨.

**Q3. Feature Store의 '훈련-서빙 스큐'가 왜 발생하고 어떻게 방지하나?**  
→ 훈련 때와 추론 때 피처 계산 로직이 달라지면 발생. Feature Store는 동일한 피처 계산 로직을 중앙화해서 두 파이프라인 모두에 제공함으로써 방지.

---

## 💬 한 줄 요약

> MLOps 플랫폼은 **모델 실험 추적(MLflow) → 파이프라인 자동화(Kubeflow) → 완전관리형 클라우드(SageMaker/GCP)**로 복잡도와 편의성이 비례한다.
