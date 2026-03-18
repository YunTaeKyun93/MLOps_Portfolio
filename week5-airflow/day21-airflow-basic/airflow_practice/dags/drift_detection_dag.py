from airflow.decorators import dag, task
from airflow.models import Variable
from datetime import datetime
import random
import requests


@dag(
    dag_id="drift_detection_dag",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["mlops", "drift"]
)
def drift_detection_dag():

    @task
    def check_model_performance():
        current_rmse = round(random.uniform(0.85, 1.2), 3)
        baseline_rmse = 0.956
        print(f"현재 RMSE: {current_rmse} / 베이스라인: {baseline_rmse}")
        return {"current_rmse": current_rmse, "baseline_rmse": baseline_rmse}

    @task
    def detect_drift(metrics: dict):
        current = metrics["current_rmse"]
        baseline = metrics["baseline_rmse"]
        threshold = baseline * 1.1

        is_drift = current > threshold
        print(f"Drift 감지: {is_drift} (현재: {current} / 임계값: {threshold:.3f})")
        return is_drift

    @task
    def retrain_model(is_drift: bool):
        if is_drift:
            print("Drift 감지됨 → 모델 재학습 시작")
            new_rmse = round(0.956 * random.uniform(0.95, 1.0), 3)
            print(f"재학습 완료 → 새 RMSE: {new_rmse}")
            return new_rmse
        else:
            print("Drift 없음 → 재학습 스킵")
            return None

    @task
    def notify(is_drift: bool, new_rmse):
        # Airflow Variable에서 Webhook URL 로드
        # Admin → Variables → slack_webhook_url 에 등록해둔 값
        webhook_url = Variable.get("slack_webhook_url")

        if is_drift:
            message = (
                f":rotating_light: *Drift 감지!*\n"
                f"> 모델 성능이 임계값(baseline × 1.1)을 초과했습니다.\n"
                f"> 재학습 완료 → 새 RMSE: `{new_rmse}`"
            )
        else:
            message = (
                f":white_check_mark: *모델 정상*\n"
                f"> Drift 없음. 재학습 불필요."
            )

        # Slack Incoming Webhook으로 메시지 전송
        response = requests.post(
            webhook_url,
            json={"text": message},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            print("Slack 알림 전송 완료")
        else:
            print(f"Slack 전송 실패: {response.status_code} / {response.text}")

    metrics = check_model_performance()
    is_drift = detect_drift(metrics)
    new_rmse = retrain_model(is_drift)
    notify(is_drift, new_rmse)


drift_detection_dag()