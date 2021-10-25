#!/bin/bash

ROOT=$(dirname $(readlink -f "$0"))

set -xe

docker run -it --rm \
  --mount type=bind,source="${ROOT}/cert.key",target=/etc/nginx/cert.key,readonly \
  --mount type=bind,source="${ROOT}/cert.crt",target=/etc/nginx/cert.crt,readonly \
  --mount type=bind,source="${ROOT}/aws_mock",target=/src/aws_mock \
  -p 443:443 \
  aws_mock
