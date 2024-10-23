FROM python:3.10.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /ems-project

# RUN apt-get update && apt-get install -y inetutils-ping

COPY requirements.txt ./

RUN pip install -U pip && pip install -r requirements.txt

COPY . ./
