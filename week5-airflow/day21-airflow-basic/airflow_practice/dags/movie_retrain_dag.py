import os
import pickle
import pandas as pd
from datetime import datetime, timedelta
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import train_test_split

import mlflow
import mlflow.sklearn

from airflow.decorators import dag, task

# MLflow 트래킹 서버 주소
# 로컬: http://host.docker.internal:5001 (Docker 내부에서 호스트 접근)
MLFLOW_TRACKING_URI = "http://172.19.0.2:5001"
MLFLOW_EXPERIMENT_NAME = "movie-recommend-svd"


@dag(
    dag_id="movie_retrain",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ml", "retrain", "movielens"],
)
def movie_retrain_pipeline():

    @task
    def load_data():
        data_path = "/opt/airflow/data/ratings.csv"

        if not os.path.exists(data_path):
            print("샘플 데이터 생성")
            sample_data = {
                "userId": list(range(1, 51)) * 20,
                "movieId": list(range(1, 21)) * 50,
                "rating": [4.0, 3.5, 5.0, 2.0, 4.5] * 200,
                "timestamp": [964982703] * 1000
            }
            df = pd.DataFrame(sample_data)
        else:
            df = pd.read_csv(data_path)

        print(f"데이터 로드 완료: {len(df)}행")
        return df.to_dict(orient="records")

    @task
    def preprocess(raw_data: list):
        df = pd.DataFrame(raw_data)

        df = df.dropna()
        df["userId"] = df["userId"].astype(int)
        df["movieId"] = df["movieId"].astype(int)
        df["rating"] = df["rating"].astype(float)
        df = df[df["rating"].between(0.5, 5.0)]
        df = df.drop_duplicates(subset=["userId", "movieId"])

        print(f"전처리 완료: {len(df)}행")
        return df.to_dict(orient="records")

    @task
    def train_model(clean_data: list):
        df = pd.DataFrame(clean_data)

        # 하이퍼파라미터 정의 (MLflow log_param용으로 변수로 분리)
        n_factors = 50
        n_epochs = 20
        test_size = 0.2

        reader = Reader(rating_scale=(0.5, 5.0))
        dataset = Dataset.load_from_df(
            df[["userId", "movieId", "rating"]], reader
        )
        trainset, testset = train_test_split(dataset, test_size=test_size)

        model = SVD(n_factors=n_factors, n_epochs=n_epochs)
        model.fit(trainset)

        predictions = model.test(testset)
        rmse = accuracy.rmse(predictions)

        # ─────────────────────────────────────────────
        # MLflow 실험 기록
        # with mlflow.start_run() = 하나의 실험 단위 (Git commit 개념)
        # 블록 안에서 기록한 param/metric/artifact가 하나의 Run으로 묶임
        # ─────────────────────────────────────────────
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

        with mlflow.start_run(run_name=f"svd-{datetime.now().strftime('%Y%m%d-%H%M')}"):

            # 하이퍼파라미터 기록 (학습 설정값)
            mlflow.log_param("n_factors", n_factors)
            mlflow.log_param("n_epochs", n_epochs)
            mlflow.log_param("test_size", test_size)
            mlflow.log_param("data_size", len(df))

            # 성능 지표 기록
            mlflow.log_metric("rmse", rmse)

            # 커스텀 태그 (실험 메타데이터)
            mlflow.set_tag("model_type", "SVD")
            mlflow.set_tag("data_source", "movielens")
            mlflow.set_tag("triggered_by", "airflow")

            print(f"✅ MLflow 실험 기록 완료 | RMSE: {rmse:.4f}")

        print(f"모델 학습 완료 | RMSE: {rmse:.4f}")

        model_bytes = pickle.dumps(model)
        return {
            "model": model_bytes.hex(),
            "rmse": rmse,
            "n_factors": n_factors,
            "n_epochs": n_epochs,
        }

    @task
    def evaluate_and_save(train_result: dict):
        new_rmse = train_result["rmse"]
        model_bytes = bytes.fromhex(train_result["model"])
        model = pickle.loads(model_bytes)

        model_path = "/opt/airflow/data/best_model.pkl"
        rmse_path = "/opt/airflow/data/best_rmse.txt"

        os.makedirs("/opt/airflow/data", exist_ok=True)

        if os.path.exists(rmse_path):
            with open(rmse_path, "r") as f:
                best_rmse = float(f.read().strip())
            print(f"이전 RMSE: {best_rmse:.4f} | 새 RMSE: {new_rmse:.4f}")
        else:
            best_rmse = float("inf")
            print(f"첫 학습 | 새 RMSE: {new_rmse:.4f}")

        if new_rmse < best_rmse:
            with open(model_path, "wb") as f:
                pickle.dump(model, f)
            with open(rmse_path, "w") as f:
                f.write(str(new_rmse))

            mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
            mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

            with mlflow.start_run(run_name=f"best-model-{datetime.now().strftime('%Y%m%d-%H%M')}"):
                mlflow.log_metric("rmse", new_rmse)
                mlflow.log_metric("rmse_improvement", best_rmse - new_rmse)
                mlflow.set_tag("status", "production_candidate")
                # mlflow.log_artifact 제거
                print(f"✅ 새 모델 MLflow 등록 완료! RMSE {best_rmse:.4f} → {new_rmse:.4f}")

                return {"saved": True, "rmse": new_rmse}
        else:
            print(f"❌ 기존 모델 유지. RMSE {new_rmse:.4f} >= {best_rmse:.4f}")
            return {"saved": False, "rmse": new_rmse}

    raw = load_data()
    cleaned = preprocess(raw)
    train_result = train_model(cleaned)
    evaluate_and_save(train_result)


movie_retrain_pipeline()