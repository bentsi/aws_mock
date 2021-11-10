import requests
from flask import Flask, Response, request


EXCLUDED_HEADERS = {"content-encoding", "content-length", "transfer-encoding", "connection"}

app = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_request(path):  # pylint: disable=unused-argument
    response = requests.request(
        method=request.method,
        url=request.url,
        data=request.get_data(),
        headers=dict(request.headers),
        cookies=request.cookies,
        allow_redirects=False,
    )
    return Response(
        response=response.content,
        status=response.status_code,
        headers=[(name, value) for name, value in response.raw.headers.items() if name.lower() not in EXCLUDED_HEADERS],
    )
