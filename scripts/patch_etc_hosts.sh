#!/bin/bash

set -xe

cat <<EOF >> /etc/hosts

### ADDED BY AWS MOCK TOOL ###
127.0.0.1   ec2.eu-north-1.amazonaws.com
127.0.0.1   scylla-qa-keystore.s3.eu-west-1.amazonaws.com
127.0.0.1   ec2.eu-west-2.amazonaws.com
EOF
