# aws_mock
Mock for AWS API

# Installation
- It developed and tested on Debian-like OSes only
- Make sure you have Python 3.10
- install the Python requirements from `requirements.txt`

# Building Docker image

## Creating CA (do it once)

    $ scripts/create_ca.sh

This step will generate `ca.passphrase`, `ca.key` and `ca.crt` files.

## Generate signed certificate

    $ scripts/create_cert.sh

This step will generate `ca.srl`, `cert.csr`, `cert.key`, and `cert.crt` files.

## Run `docker build` command

    $ docker build -t aws_mock .

# Running aws_mock server

## Install CA (do it once)

    $ scripts/install_ca.sh ca.crt

This step will add `ca.crt` to system-wide CA bundle and append it to `certifi` CA bundle installed in current 
Python environment.

If you want to make SCT work with the same CA, you need to run this script in SCT virtualenv too.

## Patch /etc/hosts

    $ sudo scripts/patch_etc_hosts.sh

## Run the  mock server 
Run using  Docker container

    $ docker run -it --rm -p 443:443 aws_mock

OR

Run aws_mock server with mapped source files using `run.sh` script:

    $ ./run.sh

It will map local `cert.key`, `cert.crt` and `aws_mock` to the Docker container.
This script is useful for development.
