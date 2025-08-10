# -----------------------------------------------------------------------------
# ARQUIVO: auth-service/Dockerfile
# -----------------------------------------------------------------------------
FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/