FROM python:3.5.2-alpine

RUN apk add --update git bash vim gcc musl-dev ca-certificates openssl-dev build-base && rm -rf /var/cache/apk/*
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /app
COPY . /app

EXPOSE 5000

CMD ["python", "main.py"]