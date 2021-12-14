FROM python:3.10.1-slim-bullseye as base

FROM base as apt_base
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq

FROM apt_base as apt_repos
RUN apt-get install -qq --no-install-recommends curl
RUN curl -fsSL https://www.mongodb.org/static/pgp/server-5.0.asc -o /etc/apt/trusted.gpg.d/mongo-server-5.0.asc
RUN echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list

FROM apt_base as python_packages
ENV PIP_NO_CACHE_DIR=1
RUN apt-get install -qq --no-install-recommends build-essential && \
    pip install poetry
ADD pyproject.toml poetry.lock ./
RUN mkdir /build && \
    poetry export -o requirements.txt && \
    pip install -r requirements.txt --root=/build --prefix=./ --ignore-installed --no-warn-script-location

FROM scratch as files
COPY configs/nginx.conf /etc/nginx/
COPY configs/uwsgi.ini configs/uwsgi_admin.ini configs/uwsgi_devmode.ini /etc/uwsgi/
COPY configs/mongod.conf configs/supervisord.conf /etc/
COPY aws_mock /src/aws_mock

FROM base
ENV PYTHONWARNINGS=ignore:unclosed \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
EXPOSE 22 443 27017
VOLUME /etc/ssl/aws_mock/ca /src/aws_mock
COPY --from=apt_repos /etc/apt /etc/apt
RUN apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -qq --no-install-recommends \
        sudo \
        nginx \
        supervisor \
        openssh-server \
        mongodb-org && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --no-create-home nginx && \
    mkdir -p /src/s3 && \
    chown nginx:nginx /src/s3 && \
    mkdir -p /var/run/sshd
COPY --from=files / /
COPY --from=python_packages /build /usr/local
WORKDIR /src
CMD ["/usr/bin/supervisord"]
