FROM apache/airflow:2.7.3

USER airflow

RUN pip install --no-cache-dir pandas scikit-learn

ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
