FROM python:3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /ems-project

# RUN apt-get update && apt-get install -y inetutils-ping

COPY requirements.txt ./

RUN python3 -m pip install -U pip

RUN pip install -r requirements.txt

COPY . ./
