FROM python:3.5.2-alpine

RUN apk add --update libxml2 libxml2-dev libxml2-utils libxslt1-dev git bash vim gcc musl-dev ca-certificates openssl-dev build-base && rm -rf /var/cache/apk/*
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /app
COPY . /app

EXPOSE 5000

CMD ["python", "main.py"]