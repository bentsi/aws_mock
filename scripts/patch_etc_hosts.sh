#!/bin/bash

set -e

echo ">>> Remove previously added hosts from /etc/hosts:"
sed -ni '/^### ADDED BY AWS MOCK TOOL ###$/,$!{p;b};w /dev/stdout' /etc/hosts
echo

if [[ "x$1" == "x--delete" ]]; then
    exit 0
fi

AWS_MOCK_IP=${1:-127.0.0.1}

echo ">>> Add hosts to /etc/hosts:"
cat <<EOF | tee --append /etc/hosts
### ADDED BY AWS MOCK TOOL ###
${AWS_MOCK_IP}  ec2.eu-north-1.amazonaws.com
${AWS_MOCK_IP}  ec2.eu-west-2.amazonaws.com
${AWS_MOCK_IP}  scylla-qa-keystore.amazonaws.com
${AWS_MOCK_IP}  scylla-qa-keystore.s3.eu-north-1.amazonaws.com
${AWS_MOCK_IP}  scylla-qa-keystore.s3.eu-west-1.amazonaws.com
EOF
