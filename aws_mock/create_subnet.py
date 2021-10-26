import logging

from flask import render_template

from aws_mock.lib import get_collection_by_resource_id, get_availability_zone_id, generate_resource_id


LOGGER = logging.getLogger(__name__)


def create_subnet(region_name: str, vpc_id: str, cidr: str, ipv6_cidr: str, availability_zone: str) -> str:
    subnet_id = generate_resource_id(resource_type="subnet")
    subnet_doc = {
        "id": subnet_id,
        "region_name": region_name,
        "vpc_id": vpc_id,
        "cidr": cidr,
        "ipv6_cidr": ipv6_cidr,
        "availability_zone": availability_zone,
        "availability_zone_id": get_availability_zone_id(availability_zone=availability_zone)
    }

    LOGGER.debug("Add subnet `%s'", subnet_id)
    get_collection_by_resource_id(resource_id=subnet_id).insert_one(subnet_doc)

    return render_template(
        "responses/create_subnet.xml",
        subnet_item=render_template("responses/subnet_item.xml", **subnet_doc),
    )
