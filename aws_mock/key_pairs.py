import logging
from uuid import uuid4
from random import getrandbits

from flask import Flask, request, render_template

from aws_mock.lib import get_aws_mock_db, get_collection_name


LOGGER = logging.getLogger(__name__)

app = Flask(__name__)


def generate_resource_id(resource_type: str, length: int = 17) -> str:
    return f"{resource_type}-{getrandbits(length * 4):x}"


def do_describe_key_pairs(key_name: str) -> tuple[str, int] | str:
    if key_pair := get_aws_mock_db()["key"].find_one({"name": key_name}):
        return render_template(
            "responses/describe_key_pairs.xml",
            key_name=key_name,
            key_pair_id=key_pair["id"],
            tags=key_pair.get("tags"),
            request_id=str(uuid4()),
        )
    return render_template(
        "responses/describe_key_pairs_not_found.xml",
        key_name=key_name,
        request_id=str(uuid4()),
    ), 400


def do_import_key_pair(key_name: str) -> str:
    key_pair_id = generate_resource_id(resource_type="key")
    get_aws_mock_db()[get_collection_name(resource_id=key_pair_id)].insert_one({"id": key_pair_id, "name": key_name})
    return render_template(
        "responses/import_key_pair.xml",
        key_name=key_name,
        key_pair_id=key_pair_id,
        request_id=str(uuid4()),
    )


@app.route("/", methods=["POST"])
def index():
    match request.form["Action"]:
        case "DescribeKeyPairs":
            key_name = request.form["KeyName.1"]
            return do_describe_key_pairs(key_name=key_name)
        case "ImportKeyPair":
            key_name = request.form["KeyName"]
            return do_import_key_pair(key_name=key_name)


@app.route("/scylla-qa-ec2.pub")
def return_scylla_qa_ec2_public_key():
    return render_template("responses/scylla-qa-ec2.pub")


@app.route("/scylla-qa-ec2")
def return_scylla_qa_ec2_private_key():
    return render_template("responses/scylla-qa-ec2")
