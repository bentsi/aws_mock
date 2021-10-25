import logging
from uuid import uuid4
from random import getrandbits

from flask import Flask, request, render_template

from aws_mock.lib import get_aws_mock_db, get_collection_name


LOGGER = logging.getLogger(__name__)

app = Flask(__name__)


def generate_resource_id(resource_type: str, length: int = 17) -> str:
    return f"{resource_type}-{getrandbits(length * 4):x}"


def do_create_security_group(group_name: str) -> str:
    security_group_id = generate_resource_id(resource_type="sg")
    get_aws_mock_db()[get_collection_name(resource_id=security_group_id)].insert_one({
        "id": security_group_id,
        "tags": {"Name": group_name},
    })
    return render_template(
        "responses/create_security_group.xml",
        security_group_id=security_group_id,
        request_id=str(uuid4()),
    )


def do_describe_security_groups() -> str:
    items = []
    for security_group in get_aws_mock_db()["sg"].find():
        items.append(render_template(
            "responses/describe_security_groups_item.xml",
            security_group_id=security_group["id"],
            tags=security_group.get("tags"),
            is_ingress_rules_added=security_group.get("is_ingress_rules_added"),
        ))
    return render_template("responses/describe_security_groups.xml", items=items, request_id=str(uuid4()))


def do_authorize_security_group_ingress(security_group_id: str) -> str:
    collection = get_aws_mock_db()[get_collection_name(resource_id=security_group_id)]
    if security_group := collection.find_one({"id": security_group_id}):
        LOGGER.debug("Add ingress rules for %s", security_group_id)
        collection.update_one(
            filter={"_id": security_group["_id"]},
            update={"$set": {"is_ingress_rules_added": True}},
        )
    return render_template(
        "responses/authorize_security_group_ingress.xml",
        security_group_id=security_group_id,
        request_id=str(uuid4()),
    )


@app.route("/", methods=["POST"])
def index():
    match request.form["Action"]:
        case "CreateSecurityGroup":
            return do_create_security_group(group_name=request.form["GroupName"])
        case "DescribeSecurityGroups":
            return do_describe_security_groups()
        case "AuthorizeSecurityGroupIngress":
            return do_authorize_security_group_ingress(security_group_id=request.form["GroupId"])
