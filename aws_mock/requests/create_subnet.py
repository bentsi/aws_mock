import logging

from aws_mock.lib import get_collection_by_resource_id, get_availability_zone_id, generate_resource_id, aws_response


LOGGER = logging.getLogger(__name__)


@aws_response
def create_subnet(region_name: str, vpc_id: str, cidr_block: str, ipv6_cidr_block: str, availability_zone: str) -> dict:
    subnet_id = generate_resource_id(resource_type="subnet")
    subnet = {
        "id": subnet_id,
        "region_name": region_name,
        "vpc_id": vpc_id,
        "cidr_block": cidr_block,
        "ipv6_cidr_block": ipv6_cidr_block,
        "availability_zone": availability_zone,
        "availability_zone_id": get_availability_zone_id(availability_zone=availability_zone),
        "tags": {},
    }

    LOGGER.debug("Add subnet `%s'", subnet_id)
    get_collection_by_resource_id(resource_id=subnet_id).insert_one(subnet)

    return {"item": subnet}
