# syntax=docker/dockerfile:1
FROM python:3.12-alpine

WORKDIR /bot

RUN apk update && apk add python3-dev gcc libc-dev libffi-dev

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["/bot/entrypoint.sh"]
