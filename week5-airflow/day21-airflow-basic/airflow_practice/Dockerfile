FROM apache/airflow:2.7.3

USER root
RUN apt-get update && apt-get install -y gcc python3-dev

USER airflow
RUN pip install --no-cache-dir pandas scikit-learn numpy scikit-surprise

ENV AIRFLOW__CORE__LOAD_EXAMPLES=False