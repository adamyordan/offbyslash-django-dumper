FROM python:2.7

RUN apt-get -qq update
RUN apt-get -yqq install nginx
RUN pip install django
RUN django-admin startproject app
RUN mkdir /app/static
COPY default /etc/nginx/sites-available
WORKDIR /app
CMD /etc/init.d/nginx start && python manage.py runserver 127.0.0.1:8000
