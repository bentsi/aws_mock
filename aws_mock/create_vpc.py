import logging

from flask import render_template

from aws_mock.lib import get_collection_by_resource_id, generate_resource_id


LOGGER = logging.getLogger(__name__)


def create_vpc(cidr: str, ipv6_support: bool, tags: dict[str, str]) -> str:
    """
        Doc: https://docs.aws.amazon.com/vpc/
    """

    vpc_id = generate_resource_id(resource_type="vpc")

    LOGGER.debug("Creating VPC `%s' with CIDR %s...", vpc_id, cidr)
    get_collection_by_resource_id(resource_id=vpc_id).insert_one({"id": vpc_id, "tags": tags})

    return render_template(
        "responses/create_vpc.xml",
        vpc_id=vpc_id,
        cidr=cidr,
        ipv6_support=ipv6_support,
    )
