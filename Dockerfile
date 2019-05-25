FROM python:3.6.8-alpine3.7
MAINTAINER Xingdao <aoqiwlzj5@gmail.com>

WORKDIR /app
COPY . /app

RUN apk add --update --no-cache mariadb-client-libs \
		mariadb-dev \
		gcc \
		musl-dev \
		libffi-dev \
		openssl-dev \
		python3-dev \
	&& pip install -r requirements.txt

EXPOSE 8000 8080

CMD ["python", "run.py", "webserver"]