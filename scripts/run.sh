#!/bin/bash

set -e

usage() {
cat <<EOF
Usage: scripts/run.sh [OPTION]... [IMAGE]
Run AWS mock server.

Options:
  -h, --help           display this help text and exit
  -d, --dev            run container in development mode (w/ mapped source files and published 443 port)
  -c, --ca-files DIR   path to the directory with CA certificate and key files
  -n, --name NAME      Docker container name (default: aws_mock)

IMAGE is a Docker container image (default: aws_mock)

EOF
}

DEV=
CA_FILES=
NAME=aws_mock

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            usage
            exit 0
            ;;
        --dev|-d)
            DEV=1
            shift
            ;;
        --ca-files|-c)
            CA_FILES="$2"
            shift 2
            ;;
        --name|-n)
            NAME="$2"
            shift 2
            ;;
        -*)
            echo "Unknown argument: $1"
            usage
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# Generic arguments.
DOCKER_ARGS=(--interactive --tty --rm --name "${NAME}")

# Environment variables.
DOCKER_ARGS+=(--env AWS_MOCK_HOSTS --env AWS_MOCK_SAVE_CA_KEY --env AWS_MOCK_DEVMODE)

if [[ -n "${CA_FILES}" ]]; then
    DOCKER_ARGS+=(--mount type=bind,source="$(cd "${CA_FILES}" && pwd -P)",target=/etc/ssl/aws_mock/ca)
    export AWS_MOCK_SAVE_CA_KEY=true
fi

if [[ -n "${DEV}" ]]; then
    env
    set -x
    DOCKER_ARGS+=(--env UWSGI_INCLUDE=/etc/uwsgi/uwsgi_devmode.ini)
    DOCKER_ARGS+=(--mount type=bind,source="$(cd $(dirname "$0")/../aws_mock && pwd -P)",target=/src/aws_mock)
    DOCKER_ARGS+=(--publish 443:443)
    export AWS_MOCK_DEVMODE=true
fi

docker run ${DOCKER_ARGS[@]} "${1:-aws_mock}"
