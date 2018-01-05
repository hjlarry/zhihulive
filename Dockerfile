FROM python:latest

ADD . /code

WORKDIR /code

RUN pip install -r requirements.txt -i https://pypi.doubanio.com/simple/

ENV DATABASE_HOST mongo
ENV DATABASE_PORT 27017
ENV REDIS_HOST redis-server
ENV REDIS_PORT 6739

EXPOSE 5000
COPY run_celery.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/run_celery.sh
RUN adduser --disabled-password --gecos '' celery_user
CMD python run.py runserver --host 0.0.0.0
