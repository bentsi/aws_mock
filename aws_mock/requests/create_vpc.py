import logging

from aws_mock.lib import get_collection_by_resource_id, generate_resource_id, aws_response


LOGGER = logging.getLogger(__name__)


@aws_response
def create_vpc(cidr_block: str, ipv6_support: bool, tags: dict[str, str]) -> dict:
    """
        Doc: https://docs.aws.amazon.com/vpc/
    """

    vpc_id = generate_resource_id(resource_type="vpc")
    vpc = {
        "id": vpc_id,
        "state": "pending",
        "cidr_block": cidr_block,
        "cidr_block_state": "associated",
        "ipv6_cidr_block": "2406:da16:5ad:8800::/56" if ipv6_support else "",
        "ipv6_cidr_block_state": "associating",
        "tags": tags,
    }
    available_state = {
        "state": "available",
        "ipv6_cidr_block_state": "associated",
    }

    LOGGER.debug("Creating VPC `%s' with CIDR %s...", vpc_id, cidr_block)
    get_collection_by_resource_id(resource_id=vpc_id).insert_one(vpc | available_state)

    return {"item": vpc}
