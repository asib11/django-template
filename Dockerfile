FROM python:3.12

ENV PYTHONUNBUFFERED 1


WORKDIR /app

RUN python -m pip install pip -U

COPY requirements.txt .


RUN pip install -r requirements.txt



