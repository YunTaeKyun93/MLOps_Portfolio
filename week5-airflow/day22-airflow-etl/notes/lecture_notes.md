# Day 22 강의 노트

**강의**: [B] Part3 Ch2-09 (24분) + [P] Part4 Ch1-01~03 (1:13)
**날짜**: 2026.03.12

---

## 오늘 들은 강의

✅ [B] Part3 Ch2-09 - 데이터 워크플로 구성 (24분)
✅ [P] Part4 Ch1-01 - 강의 소개 (10분)
✅ [P] Part4 Ch1-02 - 인프라 소개 및 구축 방법 (1) (24분)
✅ [P] Part4 Ch1-03 - 인프라 소개 및 구축 방법 (2) (18분)

---

## [B] Part3 Ch2-09 - 데이터 워크플로 구성

### 핵심 개념

- **ETL**: Extract(추출) → Transform(변환) → Load(저장) 자동화
- **Airflow DAG**: 데이터 파이프라인을 코드로 정의
- **Hook**: 외부 서비스 연결 래퍼 (BigQueryHook, GCSHook, S3Hook)
- **TaskFlow API**: `@task` 데코레이터로 선언적 Task 작성

### 강의 아키텍처 (BigQuery 기반)

```
Airflow DAG
    ↓
BigQuery (데이터 저장소)
    ↓
GCS (파일 저장)
    ↓
HuggingFace Dataset
```

### 백엔드 연결

| ML 개념                    | NestJS 개념                        |
| -------------------------- | ---------------------------------- |
| Hook                       | API wrapper / SDK                  |
| @task 데코레이터           | @UseGuards(), @UseInterceptors()   |
| extract → transform → load | 미들웨어 체인                      |
| XCom                       | 미들웨어 간 데이터 전달 (req 객체) |
| catchup=False              | 과거 스케줄 소급 실행 안함         |

### 어제 vs 오늘 Task 작성 방식

```python
# 어제 (PythonOperator 방식)
task1 = PythonOperator(
    task_id="my_task",
    python_callable=my_function,
)
task1 >> task2  # 의존성 수동 연결

# 오늘 (TaskFlow API 방식)
@task
def my_function():
    return data

result = my_function()  # 함수 호출 = 의존성 자동 연결
```

---

## [P] Part4 Ch1-01~03 - 실시간 상품 카테고리 분류 환경 구축

### 핵심 스택

- **GKE**: Google Kubernetes Engine (관리형 K8s)
- **KServe**: K8s 기반 모델 서빙 (BentoML의 K8s 버전)
- **ArgoCD**: GitOps 기반 CD 툴 (Git push → K8s 자동 배포)
- **Kafka**: 실시간 데이터 스트리밍 (메시지 큐)

### Kafka 핵심 개념

```
Producer → Kafka Topic → Consumer → ML Model → DB 저장
```

| 개념     | 의미                   | 비유           |
| -------- | ---------------------- | -------------- |
| Producer | 데이터 보내는 프로그램 | 택배 발송      |
| Kafka    | 데이터 대기열          | 컨베이어 벨트  |
| Topic    | 데이터 통로            | 택배 분류 라인 |
| Consumer | 데이터 처리 프로그램   | 택배 수령      |

### 왜 Kafka가 필요한가?

```
Kafka 없이: 1초에 500개 요청 → 서버 터짐
Kafka 있이: 대기열에 쌓아두고 순차 처리 → 안정적
```

### 커리큘럼 기준 중요도

| 스택        | 중요도    | 시기   |
| ----------- | --------- | ------ |
| Airflow DAG | 매우 중요 | 지금   |
| ArgoCD      | 중간      | Week 8 |
| KServe      | 중간      | Week 8 |
| Kafka       | 나중에    | 심화   |

---

## 💡 오늘 핵심 인사이트

**ML 시스템 = 모델 + 데이터 파이프라인**

대부분 ML 실패 이유는 모델이 아니라 데이터 파이프라인 문제.
그래서 Airflow 같은 워크플로 툴이 중요하다.

---

## ✏️ 핵심 질문 5개

### Q1. TaskFlow API(@task)와 PythonOperator의 차이는?

**A**: TaskFlow API는 `@task` 데코레이터로 선언적으로 작성, 함수 호출로 의존성 자동 연결. PythonOperator는 수동으로 Task 객체 생성 후 `>>` 로 의존성 직접 연결. TaskFlow가 더 간결하고 Python스럽다.

### Q2. XCom으로 데이터 전달할 때 왜 dict로 변환하나?

**A**: XCom은 직렬화(JSON)가 가능한 타입만 저장 가능. DataFrame은 직렬화 불가 → `to_dict(orient="records")`로 변환 후 전달.

### Q3. catchup=False가 없으면 어떻게 되나?

**A**: start_date부터 현재까지 밀린 실행을 전부 소급해서 실행함. 예: start_date가 1년 전이면 365번 실행됨. catchup=False로 소급 실행 방지.

### Q4. if_exists="replace" vs "append" 차이는?

**A**: replace = 테이블 삭제 후 재생성 (매번 최신 데이터로 교체). append = 기존 데이터에 추가. ETL에서 전체 데이터 교체는 replace, 증분 업데이트는 append 사용.

### Q5. Hook이 뭐고 왜 쓰나?

**A**: 외부 서비스(BigQuery, S3, GCS 등) 연결을 추상화한 래퍼. Connection 정보를 Airflow UI에서 관리하고 코드에서는 Hook만 사용. NestJS의 SDK 래퍼와 동일한 개념.

---

## 💬 오늘 강의 한 줄 요약

> ETL = Extract→Transform→Load 자동화, @task 데코레이터로 선언적 파이프라인 구성, 데이터 파이프라인이 ML 시스템의 핵심이다.
