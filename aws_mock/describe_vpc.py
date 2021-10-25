from uuid import uuid4

import logging
import string
import random

from flask import Flask, request, render_template
from werkzeug.datastructures import ImmutableMultiDict
from aws_mock.lib import get_collection_name, get_aws_mock_db, extract_tags

app = Flask(__name__)
LOGGER = logging.getLogger(__name__)


def generate_resource_id(prefix="vpc"):
    rand_id = "".join(random.choices(population=string.ascii_lowercase + string.digits, k=17))
    return f"{prefix}-{rand_id}"


def describe_vpc(request_data: ImmutableMultiDict[str, str]) -> str:
    """
        Doc: https://docs.aws.amazon.com/vpc/
    """
    cidr = "10.0.0.0/16"
    vpc_id = request_data["VpcId"]
    db = get_aws_mock_db()
    collection = db[get_collection_name(vpc_id)]
    collection.insert({
        "id": vpc_id,
        "tags": extract_tags(request.form),
    })
    return render_template("responses/describe_vpc.xml",
                           request_id=str(uuid4()),
                           vpc_id=vpc_id,
                           cidr=cidr,
                           return_content=True,)


@app.route("/", methods=['POST'])
def index():
    match request.form["Action"]:
        case "DescribeVpcs":
            return describe_vpc(request_data=request.form)
