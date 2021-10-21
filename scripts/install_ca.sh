#!/bin/bash

set -xe

if [[ "x$1" == "x" ]]; then
  echo "missed parameter: path to CA certificate"
  exit 1
fi

CA_CERT="$1"
CERTIFI_CA_BUNDLE=$(python -c "import pathlib as p, certifi as c; print(p.Path(c.__file__).with_name('cacert.pem'))")

sudo cp "${CA_CERT}" /usr/local/share/ca-certificates/
sudo update-ca-certificates --fresh
sudo cat "${CA_CERT}" >> ${CERTIFI_CA_BUNDLE}
