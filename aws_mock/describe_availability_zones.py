from urllib.parse import urlparse
from uuid import uuid4

from flask import request, Flask, render_template

from aws_mock.lib import get_region_name_from_hostname, get_short_region_name

app = Flask(__name__)


def describe_availability_zones(hostname: str) -> str:
    region_name = get_region_name_from_hostname(hostname=hostname)
    short_region_name = get_short_region_name(region_name)
    return render_template(
        template_name_or_list='responses/describe_availability_zones.xml',
        request_id=str(uuid4()),
        region_name=region_name,
        short_region_name=short_region_name)


@app.route("/", methods=["POST"])
def index():
    match request.form["Action"]:
        case "DescribeAvailabilityZones":
            return describe_availability_zones(hostname=request.headers['Host'])


if __name__ == "__main__":
    app.run(debug=True, port=8888)
