import datetime
from textwrap import dedent

from flask import Response


PUBLIC_KEY = dedent(
    """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCn/ong1NEz4cQCHf8TjzRXD5DUQ4McFBXpQj0TN8ART6LF3jVeDYSZlYRlnDMQvMfZkNJWlDCa
    knS5fWQzp50/r/7ACw2RI/aFpZHshGMm2iLXaLMyVqeW5T3pWpU5nr5j9hzdVqv1zuzhq1qE3r/yRM3nVIotH+6S87ZmFhISeMgNbhC2AFH3O9ntt+B
    iQ1uAGJkozg3pxhdF0GI0d3zQNv4P0krChqHSf355YyAVzBpQk2t+8Y1fmJM6bX+bmIRvvsXxCGjqbdoLGrJHmdWwej8K8W0Ov9xUwg8pWbji5+dmCP
    dWUQPaAemefVql9xWHPnc2AGVe4E2H5OmJRnpwND84QLCHpvXyyyipnaI+a4tKjPBwp3oSA4pOwbdwh/f6/l73Rl/FO9k2N4Uz651gVNuL6IxP79t9H
    PMTsYkTnXGG3WrjPMZ5za7u/CjtQ+DXd1nRGxqbmlybtbXooPb2TPybs08R3vTpsXx+x3HgpBncTiWBGkl6Wm/X0zLyGksGG/9sgnSD3d4n9d/qEg8W
    M+Nptw4vQjzI4pI24d0sAAlVrM3hqDq7KsiT2TgepiwdnQuMtL2I05CzjviQzBVlr0lSkoui86POlRkBMmjpfzxeGIhCMagpB/0BkkF0kqNWJBE1OVE
    EjJUAoV88l5SyhvOV6PAal31GgtKw7qyj3Q== qa-bot@scylladb.com""")

PRIVATE_KEY = dedent(
    """-----BEGIN OPENSSH PRIVATE KEY-----
    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
    -----END OPENSSH PRIVATE KEY-----
    """)


def _return_response(body):
    resp = Response(body)
    resp.headers['Accept-Ranges'] = 'bytes'
    resp.headers['Content-Length'] = len(body)
    resp.headers['Content-Type'] = 'binary/octet-stream'
    time_now = datetime.datetime.utcnow().strftime('%a, %d %b %H:%m:%S GMT')
    resp.headers['Date'] = time_now
    resp.headers['ETag'] = '\'"f2bf16ed96e3e0bc9ad35e8146c3149e"\''
    resp.headers['Last-Modified'] = time_now
    resp.headers['Server'] = 'AmazonS3'
    resp.headers['x-amz-id-2'] = 'JuMP25y3NBEs4wU9UuHA2/EmrgvxQFlGbhHork+z3e3KONtm5iv0jNP7+BBg73+CQUlU6NyI3dE='
    resp.headers['x-amz-request-id'] = 'TFXDYNQWSMNPXXFZ'
    resp.headers['x-amz-server-side-encryption'] = 'AES256'

    return resp


def get_public_key():
    return _return_response(PUBLIC_KEY)


def get_private_key():
    return _return_response(PRIVATE_KEY)
