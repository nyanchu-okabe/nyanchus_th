#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
DJANGO_SUPERUSER_USERNAME=nyanchu DJANGO_SUPERUSER_EMAIL=nyanchu.okabe@gmail.com DJANGO_SUPERUSER_PASSWORD='OkabeDa_0709!' python manage.py createsuperuser --noinput
echo nyanchu
echo 'OkabeDa_0709!'
