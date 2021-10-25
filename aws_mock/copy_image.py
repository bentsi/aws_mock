from flask import Flask, request, render_template
from uuid import uuid4
from aws_mock.lib import get_collection_name, get_aws_mock_db, get_region_name_from_hostname
import logging
import random
import string

LOGGER = logging.getLogger(__name__)

app = Flask(__name__)


def generate_resource_id(prefix="ami"):
    rand_id = "".join(random.choices(population=string.ascii_lowercase + string.digits, k=17))
    return f"{prefix}-{rand_id}"


def copy_images(hostname: str, request_data: dict) -> str:
    source_region = request_data["SourceRegion"]
    source_ami_id = request_data["SourceImageId"]
    region = get_region_name_from_hostname(hostname=hostname)
    ami_id = generate_resource_id(prefix="ami")
    request_id = str(uuid4())
    LOGGER.debug("Copying image from region=%s id=%s to region=%s id=%s...",
                 source_region, source_ami_id, region, ami_id)
    db = get_aws_mock_db()
    collection = db[get_collection_name(ami_id)]
    collection.insert({
        "id": ami_id,
        "region": region
    })
    return render_template("responses/copy_image.xml", image_id=ami_id, request_id=request_id)


@app.route("/", methods=["POST"])
def index():
    match request.form["Action"]:
        case "CopyImage":
            return copy_images(hostname=request.headers["Host"], request_data=request.form)
