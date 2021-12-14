# aws_mock


Mock for AWS API.

[![License: Apache2](https://img.shields.io/github/license/scylladb/aws_mock.svg)](https://github.com/scylladb/seastar/blob/master/LICENSE)

# Installation

## System requirements

- It developed and tested on Debian-like OSes only
- You need Docker to build and run the server
- You need OpenSSL' `openssl` binary and GNU `sed` for scripts

## Build `aws_mock` Docker image

    $ docker build -t aws_mock .

## For development

- Make sure you have Python 3.10
- [Install Poetry](https://python-poetry.org/docs/#installation)
- Install the Python requirements using poetry: `$ poetry install`

# Run AWS mock server

## How to provide a list of AWS hosts to mock

The AWS Mock server use `AWS_MOCK_HOSTS` environment variable as a space-separated list of hosts:

    $ export AWS_MOCK_HOSTS="ec2.eu-north-1.amazonaws.com my-bucket.s3.amazonaws.com"

## Run Docker container

    $ scripts/run.sh

Default Docker container name is `aws_mock` but you can provide it using `--name` option of the script.

## Reusing CA files between runs

    $ mkdir ./.aws_mock_ca
    $ scripts/run.sh --ca-files ./.aws_mock_ca

This command will generate all required keys and certificates on the first run and store them to
`./.aws_mock_ca` directory.  On consequent runs it'll reuse CA files but regenerate server key and certificate.

## Run Docker container in development mode

    $ scripts/run.sh --dev

This command will map local `aws_mock` to the Docker container and publish port 443 to localhost.
Also, it'll monitor for source files and restart uWSGI on changes.

You can combine both `--ca-files` and `--dev` options together.

## Patch /etc/hosts

    $ scripts/mocked-hosts.sh --patch-etc-hosts

This command will extract hosts from the AWS mock server SSL certificate and add them to `/etc/hosts` file.
By default, it uses 127.0.0.1 as IP address, and it's OK if you run Docker container in development mode, but
you can specify any IP address using `--ip` option if port 443 not published to the localhost:

    $ scripts/mocked-hosts.sh --patch-etc-hosts --ip 172.17.0.2

or get IP address from a Docker container via `--container` option:

    $ scripts/mocked-hosts.sh --patch-etc-hosts --container aws_mock

## Install AWS Mock CA certificate to the localhost

    $ curl -k https://aws-mock.itself/install-ca.sh | bash

This command will add AWS Mock CA certificate to /usr/local/share/ca-certificates and to the `certifi`'s CA bundle
in current Python environment.

Note, that it assumes you use a Debian-like Linux distribution and have already patched `/etc/hosts`.

# Complete example

> **⚠️** Note, it's supposed to run on a Debian-like OS.

Build and run the AWS Mock server:

    $ docker build -t aws_mock .
    $ mkdir ./.aws_mock_ca
    $ export AWS_MOCK_HOSTS="ec2.eu-north-1.amazonaws.com my-bucket.s3.amazonaws.com"
    $ scripts/run.sh --ca-files ./.aws_mock_ca --dev

In another terminal:

    $ scripts/mocked-hosts.sh --patch-etc-hosts
    $ curl -k https://aws-mock.itself/install-ca.sh | bash
    $ docker exec aws_mock bash -c 'mkdir /src/s3/my-bucket; echo Hello > /src/s3/my-bucket/hello'
    $ python
    Python 3.10.0 (default, Oct  5 2021, 06:22:43) [GCC 7.5.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import boto3, pprint
    >>> ec2 = boto3.client("ec2", region_name="eu-north-1")
    >>> pprint.pprint(ec2.describe_instances())
    {'Reservations': [{'Groups': [],
                   'Instances': [],
                   'OwnerId': '...',
                   'ReservationId': '...'}],
     'ResponseMetadata': {'HTTPHeaders': {'connection': 'keep-alive',
                                          'content-length': '441',
                                          'content-type': 'text/html; '
                                                          'charset=utf-8',
                                          'date': '...',
                                          'server': 'nginx/1.18.0'},
                          'HTTPStatusCode': 200,
                          'RequestId': '...',
                          'RetryAttempts': 0}
    >>> s3 = boto3.resource("s3")
    >>> s3.Object("my-bucket", "hello").get()["Body"].read()
    b'Hello\n'
    >>>^D
    $ scripts/mocked-hosts.sh --remove
