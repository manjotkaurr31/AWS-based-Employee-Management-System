FROM python:3.11-slim

WORKDIR /app

COPY app/ /app/app/

RUN pip install --no-cache-dir fastapi uvicorn gunicorn sqlalchemy psycopg2-binary boto3

CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]
