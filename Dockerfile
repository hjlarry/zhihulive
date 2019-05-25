FROM tnir/mysqlclient:latest
MAINTAINER Xingdao <aoqiwlzj5@gmail.com>

WORKDIR /app
COPY . /app

RUN apk add --update --no-cache gcc \
		libffi-dev \
		openssl-dev \
		python3-dev \
	&& pip install -r requirements.txt

EXPOSE 8000 8080

CMD ["python", "run.py", "webserver"]