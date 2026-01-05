FROM python:3.12-slim

WORKDIR /worker

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt /worker/requirements.txt
RUN pip install --no-cache-dir -r /worker/requirements.txt

COPY worker.py /worker/worker.py

CMD ["celery", "-A", "worker.celery_app", "worker", "-Q", "ai_tasks", "--loglevel=info"]
