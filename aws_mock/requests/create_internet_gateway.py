import logging

from aws_mock.lib import get_collection_by_resource_id, generate_resource_id, aws_response


LOGGER = logging.getLogger(__name__)


@aws_response
def create_internet_gateway() -> dict:
    gateway_id = generate_resource_id(resource_type="igw")
    gateway = {"id": gateway_id, "attachments": [], "tags": {}}

    LOGGER.debug("Add internet gateway `%s'", gateway_id)
    get_collection_by_resource_id(resource_id=gateway_id).insert_one(gateway)

    return {"item": gateway}
