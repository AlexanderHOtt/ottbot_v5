FROM python:3.10.5-alpine

WORKDIR /app

ENV PYTHONUNBUFFERED 1

# TODO: remove git repos from req.txt for prod
RUN apk add --no-cache --virtual .build-deps git gcc python3-dev musl-dev build-base

RUN pip install pip -U

COPY requirements.txt .
RUN pip install -r requirements.txt -U

COPY ottbot ottbot/
