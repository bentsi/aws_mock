from uuid import uuid4

import logging
import string
import random

from flask import Flask, request, render_template
from werkzeug.datastructures import ImmutableMultiDict
from aws_mock.lib import get_collection_name, get_aws_mock_db, extract_tags


app = Flask(__name__)
LOGGER = logging.getLogger(__name__)


def generate_resource_id(prefix="i"):
    rand_id = "".join(random.choices(population=string.ascii_lowercase + string.digits, k=17))
    return f"{prefix}-{rand_id}"


def run_instances(request_data: ImmutableMultiDict[str, str]) -> str:
    """
        Doc: https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_RunInstances.html
    """
    num_instances = int(request_data["MaxCount"])
    LOGGER.debug(f"Creating %s instances...", num_instances)
    db = get_aws_mock_db()
    items = []
    for _ in range(num_instances):
        instance_id = generate_resource_id(prefix="i")
        collection = db[get_collection_name(instance_id)]
        collection.insert({
            "id": instance_id,
            "tags": extract_tags(request.form),
        })
        items.append(render_template("responses/run_instances_item.xml", instance_id=instance_id))
    return render_template("responses/run_instances.xml", items=items,  request_id=str(uuid4()))


@app.route("/", methods=['POST'])
def index():
    action = request.form["Action"]
    match request.form["Action"]:
        case "RunInstances":
            return run_instances(request_data=request.form)
        case _:
            return f"Unknown action: {action}", 400
