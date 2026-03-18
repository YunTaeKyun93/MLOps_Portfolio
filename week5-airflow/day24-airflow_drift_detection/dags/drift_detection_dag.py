from airflow.decorators import dag, task
from datetime import datetime
import random


@dag(
  dag_id="drift_detection_dag",
  schedule="@daily",
  start_date=datetime(2026,1,1),
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
  def detect_drift(metrics : dict):
    current = metrics["current_rmse"]
    baseline = metrics["baseline_rmse"]
    threshold = baseline  * 1.1

    is_drift = current > threshold
    print(f"Drift 감지: {is_drift} (현재: {current} / 임계값: {threshold})")
    return is_drift
  
  @task
  def retrain_model(is_drift : bool):
    if is_drift:
            print("Drift 감지됨 → 모델 재학습 시작")
            new_rmse = round(0.956 * random.uniform(0.95, 1.0), 3)
            print(f"재학습 완료 → 새 RMSE: {new_rmse}")
            return new_rmse
    else:
            print("Drift 없음 → 재학습 스킵")
            return None

  @task
  def notify(is_drift : bool, new_rmse):
      if is_drift:
            print(f"[알림] Drift 감지 → 재학습 완료. 새 RMSE: {new_rmse}")
      else:
            print("[알림] 모델 정상. 재학습 불필요.")


  metrics = check_model_performance()
  is_drift = detect_drift(metrics)
  new_rmse  = retrain_model(is_drift)
  notify(is_drift, new_rmse)

drift_detection_dag()