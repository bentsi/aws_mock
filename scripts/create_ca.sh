#!/bin/bash

set -xe

[[ -f .ca_created ]] && exit 0

python -c "import uuid; print(str(uuid.uuid4())[:8])" > ca.passphrase
openssl genrsa -des3 -out ca.key -passout file:ca.passphrase 2048
openssl req -x509 -new -nodes -batch -key ca.key -passin file:ca.passphrase -sha256 -days 1825 -out ca.crt

touch .ca_created
