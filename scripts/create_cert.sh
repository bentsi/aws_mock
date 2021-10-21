#!/bin/bash

set -xe

openssl genrsa -out cert.key 2048
openssl req -new -batch -key cert.key -out cert.csr
openssl x509 -req \
    -passin file:ca.passphrase -CA ca.crt -CAkey ca.key -CAcreateserial \
    -in cert.csr -out cert.crt -days 825 -extfile configs/cert.ext
