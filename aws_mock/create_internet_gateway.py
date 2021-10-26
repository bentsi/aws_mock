import logging

from flask import render_template

from aws_mock.lib import get_collection_by_resource_id, generate_resource_id


LOGGER = logging.getLogger(__name__)


def create_internet_gateway():
    gateway_id = generate_resource_id(resource_type="igw")

    LOGGER.debug("Add internet gateway `%s'", gateway_id)
    get_collection_by_resource_id(resource_id=gateway_id).insert_one({"id": gateway_id})

    return render_template(
        "responses/create_internet_gateway.xml",
        item=render_template("responses/internet_gateway_item.xml", id=gateway_id)
    )
