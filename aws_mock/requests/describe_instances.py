import logging

from aws_mock.lib import get_collection_by_resource_id, aws_response


LOGGER = logging.getLogger(__name__)


@aws_response
def describe_instances(instance_ids: list[str]) -> dict:
    """
        Action=DescribeInstances&Version=2016-11-15&InstanceId.1=i-08cafe5e67f1a0bd2
        Doc: https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeInstances.html
    """
    if not instance_ids:  # no instances provided return empty list
        return {"items": []}

    LOGGER.debug("Looking for instances with ids: %s ...", instance_ids)
    instances = list(get_collection_by_resource_id(resource_id=instance_ids[0]).find({"id": {"$in":  instance_ids}}))
    LOGGER.debug("Found instances: %s", instances)

    return {"items": instances}
