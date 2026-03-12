import os 
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from airflow.decorators import dag, task 

@dag(
    dag_id="movielens_etl",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["etl", "movielens"],
)

def movielens_etl_pipeline():

  @task
  def extract():
    data_path = "opt/airflow/data/ratings.csv"

    if not os.path.exists(data_path):
          print("ratings.csv 없음 → 샘플 데이터 생성")
          sample_data = {
                "userId": [1, 1, 2, 2, 3, 3, None, 4],
                "movieId": [1, 2, 1, 3, 2, 3, 4, None],
                "rating": [4.0, 3.5, 5.0, 2.0, 4.5, 3.0, 4.0, 3.5],
                "timestamp": [
                    964982703, 964981247, 964982224,
                    964983815, 964982931, 964982400,
                    964982400, 964982400
                ]
            }
          
          df  = pd.DataFrame(sample_data)
    else:
       print(f"CSV 로드: {data_path}")
       df = pd.read_csv(data_path)
    print(f"Extract 완료: {len(df)}행")
    return df.to_dict(orient="records")
  
  @task
  def transform(raw_data:list):
    df = pd.DataFrame(raw_data)

    print(f"Transform 전: {len(df)}행")
    print(f"결측치 현황:\n{df.isnull().sum()}")

    df = df.dropna()

    df["userId"] = df["userId"].astype(int)
    df["movieId"] = df["movieId"].astype(int)
    df["rating"] = df["rating"].astype(float)
    df["timestamp"] = df["timestamp"].astype(int)

    df = df[df["rating"].between(0.5, 5.0)]

    before = len(df)
    df = df.drop_duplicates(subset=["userId", "movieId"])
    print(f"중복 제거: {before - len(df)}행 제거")
    print(f"Transform 후: {len(df)}행")

    return df.to_dict(orient="records")
  
  
  @task
  def load(clean_data: list):
        df = pd.DataFrame(clean_data)

        db_path = "/opt/airflow/data/movielens.db"
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        conn = sqlite3.connect(db_path)
        df.to_sql("ratings", conn, if_exists="replace", index=False)

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ratings")
        count = cursor.fetchone()[0]
        conn.close()

        print(f"Load 완료: {count}행 저장 → {db_path}")
        return {"saved_rows": count, "db_path": db_path}

  raw = extract()
  cleaned = transform(raw)
  load(cleaned)


movielens_etl_pipeline()
