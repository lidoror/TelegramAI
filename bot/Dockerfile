FROM python:3.8.12-slim-buster
WORKDIR /app

COPY ../config.json .

RUN mkdir "bot"

COPY . ./bot

RUN pip install -r requirements.txt

CMD ["python3", "-m", "bot.app"]