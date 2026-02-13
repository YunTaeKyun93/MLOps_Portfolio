FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt



COPY src ./src/
COPY outputs ./outputs/

CMD ["python", "src/predict.py"]