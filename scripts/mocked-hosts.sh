#!/bin/bash

set -e

usage() {
cat <<EOF
Usage: scripts/mocked_hosts.sh [OPTION]...
Extract hosts from the AWS mock server certificate and patch /etc/hosts

Options:
  -h, --help              display this help text and exit
  -d, --remove            remove mocked hosts from /etc/hosts
  -p, --patch-etc-hosts   patch /etc/hosts file to redirect traffic to the AWS mock server
  -l, --list              list hosts extracted from the server certificate (default)
  -i, --ip IP             specify IP address of the AWS Mock server
  -c, --container NAME    get IP address of the AWS Mock server from a Docker container

Default IP address of the AWS mock server is 127.0.0.1

EOF
}

REMOVE=
GET_HOSTS=
LIST=
PATCH_ETC_HOSTS=
AWS_MOCK_IP=127.0.0.1

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            usage
            exit 0
            ;;
        --remove|-d)
            REMOVE=1
            shift
            ;;
        --patch-etc-hosts|-p)
            REMOVE=1
            GET_HOSTS=1
            PATCH_ETC_HOSTS=1
            shift
            ;;
        --list|-l)
            GET_HOSTS=1
            LIST=1
            shift
            ;;
        --ip|-i)
            AWS_MOCK_IP="$2"
            shift 2
            ;;
        --container|-c)
            AWS_MOCK_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$2")
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            usage
            exit 1
            ;;
    esac
done

# Default action.
if [[ -z "$REMOVE" && -z "$GET_HOSTS" && -z "$LIST" && -z "$PATCH_ETC_HOSTS" ]]; then
    GET_HOSTS=1
    LIST=1
fi

if [[ -n "${REMOVE}" ]]; then
  echo ">>> Following lines removed from /etc/hosts:"
  sudo sed -ni '/^### ADDED BY AWS MOCK TOOL ###$/,$!{p;b};w /dev/stdout' /etc/hosts
  echo
fi

if [[ -n "${GET_HOSTS}" ]]; then
    MOCKED_HOSTS=$(openssl s_client -connect "${AWS_MOCK_IP}:443" </dev/null 2>/dev/null \
                   | openssl x509 -noout -ext subjectAltName \
                   | grep -Po '(?<=DNS:)[^,]+')
fi

if [[ -n "${LIST}" ]]; then
    echo ">>> Hosts extracted from ${AWS_MOCK_IP}:443 server certificate:"
    echo "${MOCKED_HOSTS}"
    echo
fi

if [[ -n "${PATCH_ETC_HOSTS}" ]]; then
    echo ">>> Add following lines to /etc/hosts:"
    (
        echo '### ADDED BY AWS MOCK TOOL ###'
        for host in ${MOCKED_HOSTS}; do
           echo "${AWS_MOCK_IP}  ${host}"
        done
    ) | sudo tee -a /etc/hosts
    echo
fi
