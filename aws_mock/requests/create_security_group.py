import logging

from aws_mock.lib import get_collection_by_resource_id, generate_resource_id, aws_response


LOGGER = logging.getLogger(__name__)


@aws_response
def create_security_group(group_name: str) -> dict:
    security_group_id = generate_resource_id(resource_type="sg")

    LOGGER.debug("Add security group `%s' with name `%s'", security_group_id, group_name)
    get_collection_by_resource_id(resource_id=security_group_id).insert_one({
        "id": security_group_id,
        "tags": {"Name": group_name},
    })

    return {"security_group_id": security_group_id}
