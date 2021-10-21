FROM python:3.10.0-slim-bullseye

RUN apt-get update -qq
RUN apt-get install -qq --no-install-recommends build-essential nginx supervisor

EXPOSE 443

RUN useradd --no-create-home nginx

COPY requirements.txt /src/requirements.txt
WORKDIR /src
RUN pip install -r requirements.txt

COPY cert.crt cert.key configs/nginx.conf /etc/nginx/
COPY configs/uwsgi.ini /etc/uwsgi/
COPY configs/supervisord.conf /etc/

COPY aws_mock /src/aws_mock

CMD ["/usr/bin/supervisord"]
