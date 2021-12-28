FROM python:3.8.3-slim-buster
LABEL maintainer="Concordat Team"

COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt -r requirements-dev.txt

ENV APP=/concordat
ENV PYTHONPATH=$PYTHONPATH:${APP}

COPY concordat concordat
