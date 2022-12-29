FROM python:3.8.12-slim-buster
WORKDIR /app

COPY ./config.json .

COPY ./utils.py .

WORKDIR /app/worker

COPY ./worker .


RUN pip install -r requirements.txt

WORKDIR /app

CMD ["python3", "-m", "worker.app"]