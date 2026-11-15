FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app/src RETENTION_DATA_PATH=/app/data/snapshots.csv
RUN python -m retention_lab.cli demo --output /app/data/snapshots.csv
CMD ["uvicorn", "retention_lab.api:app", "--host", "0.0.0.0", "--port", "8000"]
