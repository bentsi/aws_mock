import logging
from datetime import datetime

from aws_mock.lib import (
    aws_response,
    generate_resource_id,
    get_aws_mock_db,
    get_aws_mock_server_ip,
    get_collection_by_resource_id,
)


LOGGER = logging.getLogger(__name__)


@aws_response
def run_instances(count: int, instance_spec: dict[str, str]) -> dict | tuple[str, int]:
    """
        Doc: https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_RunInstances.html
    """
    subnet_id = instance_spec["subnet_id"]
    subnet = get_collection_by_resource_id(resource_id=subnet_id).find_one({"id": subnet_id})
    if not subnet:
        return f"Subnet `{subnet_id}' not found", 400

    security_group_id = instance_spec["security_group_id"]
    security_group = get_collection_by_resource_id(resource_id=security_group_id).find_one({"id": security_group_id})
    if not security_group:
        return f"Security group `{security_group_id}' not found", 400

    instance_spec = instance_spec | {
        "region_name": subnet["region_name"],
        "availability_zone": subnet["availability_zone"],
        "vpc_id": subnet["vpc_id"],
        "security_group_name": security_group["tags"]["Name"],
        "public_ip": get_aws_mock_server_ip(),
        "launch_time": f"{datetime.utcnow():%Y-%m-%dT%H:%M:%S}.000Z",
    }
    running_state = {
        "instance_state_code": "16",
        "instance_state": "running",
    }

    LOGGER.debug("Creating %s instances...", count)
    instances = [instance_spec | {"id": generate_resource_id(resource_type="i")} for _ in range(count)]
    get_aws_mock_db()["i"].insert_many(instance | running_state for instance in instances)

    return {"items": instances}
