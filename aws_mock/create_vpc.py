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


def create_vpc(request_data: ImmutableMultiDict[str, str]) -> str:
    """
        Doc: https://docs.aws.amazon.com/vpc/
    """
    cidr = request_data["CidrBlock"]
    ipv6_support = bool(request_data["AmazonProvidedIpv6CidrBlock"])
    LOGGER.debug(f"Creating VPC with CIDR %s...", cidr)
    db = get_aws_mock_db()

    vpc_id = generate_resource_id(prefix="vpc")
    collection = db[get_collection_name(vpc_id)]
    collection.insert({
        "id": vpc_id,
        "tags": extract_tags(request.form),
    })
    return render_template("responses/create_vpc.xml",
                           request_id=str(uuid4()),
                           vpc_id=vpc_id,
                           cidr=cidr,
                           ipv6_support=ipv6_support)


@app.route("/", methods=['POST'])
def index():
    match request.form["Action"]:
        case "CreateVpc":
            return create_vpc(request_data=request.form)
