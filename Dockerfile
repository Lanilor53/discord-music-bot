# syntax=docker/dockerfile:1
FROM python:alpine3.14
RUN apk add --no-cache g++ make libffi-dev ffmpeg opus-dev
WORKDIR /discord-music-bot
COPY . .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
CMD ["python", "main.py"]

