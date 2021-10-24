FROM python:3.10.0-slim-bullseye

RUN apt-get update -qq
RUN apt-get install -qq --no-install-recommends build-essential nginx supervisor gnupg wget
RUN wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
RUN echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list
RUN apt-get update -qq
RUN apt-get install -qq --no-install-recommends mongodb-org

VOLUME /var/lib/mongodb

EXPOSE 443 27017

RUN useradd --no-create-home nginx

COPY requirements.txt /src/requirements.txt
WORKDIR /src
RUN pip install -r requirements.txt

COPY cert.crt cert.key configs/nginx.conf /etc/nginx/
COPY configs/uwsgi.ini /etc/uwsgi/
COPY configs/mongod.conf /etc/
COPY configs/supervisord.conf /etc/

COPY aws_mock /src/aws_mock

CMD ["/usr/bin/supervisord"]
