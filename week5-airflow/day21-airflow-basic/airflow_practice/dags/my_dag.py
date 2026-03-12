from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score


default_args = {
    "owner": "airflow",
    "start_date": datetime(2023,1,1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

dag = DAG(
    dag_id="model_training_selection",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
)


def feature_engineering(ti):

    from sklearn.datasets import load_iris

    iris = load_iris()

    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target)

    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3)

    ti.xcom_push(key="X_train", value=X_train.to_json())
    ti.xcom_push(key="X_test", value=X_test.to_json())
    ti.xcom_push(key="y_train", value=y_train.to_json())
    ti.xcom_push(key="y_test", value=y_test.to_json())


def train_model(model_name, ti):

    X_train = pd.read_json(ti.xcom_pull(key="X_train", task_ids="feature_engineering"))
    X_test = pd.read_json(ti.xcom_pull(key="X_test", task_ids="feature_engineering"))
    y_train = pd.read_json(ti.xcom_pull(key="y_train", task_ids="feature_engineering"), typ="series")
    y_test = pd.read_json(ti.xcom_pull(key="y_test", task_ids="feature_engineering"), typ="series")

    if model_name == "RandomForest":
        model = RandomForestClassifier()
    else:
        model = GradientBoostingClassifier()

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    acc = accuracy_score(y_test, pred)

    ti.xcom_push(key=f"performance_{model_name}", value=acc)


def select_best_model(ti):

    rf = ti.xcom_pull(key="performance_RandomForest", task_ids="train_rf")
    gb = ti.xcom_pull(key="performance_GradientBoosting", task_ids="train_gb")

    best = "RandomForest" if rf > gb else "GradientBoosting"

    Variable.set("best_model", best)

    print("Best model:", best)

    return best


with dag:

    t1 = PythonOperator(
        task_id="feature_engineering",
        python_callable=feature_engineering
    )

    t2 = PythonOperator(
        task_id="train_rf",
        python_callable=train_model,
        op_kwargs={"model_name":"RandomForest"}
    )

    t3 = PythonOperator(
        task_id="train_gb",
        python_callable=train_model,
        op_kwargs={"model_name":"GradientBoosting"}
    )

    t4 = PythonOperator(
        task_id="select_best_model",
        python_callable=select_best_model
    )

    t1 >> [t2,t3] >> t4
