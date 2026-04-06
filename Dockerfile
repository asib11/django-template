FROM python:3.10

ENV PYTHONUNBUFFERED 1


WORKDIR /app

RUN python -m pip install pip -U

COPY requirements.txt .


RUN pip install -r requirements.txt



