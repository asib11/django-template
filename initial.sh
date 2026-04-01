#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt 
python manage.py makemigrations
python manage.py migrate
