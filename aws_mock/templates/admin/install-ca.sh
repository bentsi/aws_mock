#!/bin/bash

set -xe

AWS_MOCK_CA_CERT=/usr/local/share/ca-certificates/aws_mock.crt
CERTIFI_CA_BUNDLE=$(python -c "import pathlib as p, certifi as c; print(p.Path(c.__file__).with_name('cacert.pem'))")

echo ">>> Following lines removed from $CERTIFI_CA_BUNDLE:"
sudo sed -ni 'N;/^\n# Issuer: CN=AWS Mock CA$/,/-----END CERTIFICATE-----/!{p;b};w /dev/stdout' "$CERTIFI_CA_BUNDLE"
echo

cat << EOF | sudo tee "$AWS_MOCK_CA_CERT" | sudo tee -a "$CERTIFI_CA_BUNDLE"

# Issuer: CN=AWS Mock CA
# Subject: CN=AWS Mock CA
{{ certificate }}
EOF

sudo update-ca-certificates --fresh
