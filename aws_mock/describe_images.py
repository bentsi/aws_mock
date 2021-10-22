from flask import Flask, request, render_template
from uuid import uuid4
from aws_mock.lib import get_collection_name, get_aws_mock_db, get_region_name_from_hostname
import logging

LOGGER = logging.getLogger(__name__)

app = Flask(__name__)


def describe_images(hostname) -> str:
    request_id = str(uuid4())
    master_region = "eu-west-2"
    region = get_region_name_from_hostname(hostname=hostname)
    db = get_aws_mock_db()
    LOGGER.debug("Searching for saved images...")
    ami_ids_count = db[get_collection_name("ami-")].count()
    if region == master_region or ami_ids_count:
        LOGGER.debug("Describing default image...")
        ami = render_template("responses/describe_images_default_ami.xml")
    else:
        LOGGER.debug("No images were found.")
        ami = ""
    return render_template("responses/describe_images.xml", ami=ami, request_id=request_id)


@app.route("/", methods=["POST"])
def index():
    match request.form["Action"]:
        case "DescribeImages":
            return describe_images(hostname=request.headers["Host"])
