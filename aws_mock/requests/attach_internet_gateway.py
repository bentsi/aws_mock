import logging

from aws_mock.lib import get_collection_by_resource_id, aws_response


LOGGER = logging.getLogger(__name__)


@aws_response
def attach_internet_gateway(gateway_id: str, vpc_id: str) -> None:
    collection = get_collection_by_resource_id(resource_id=gateway_id)
    if gateway := collection.find_one({"id": gateway_id}):
        LOGGER.debug("Attach `%s' to `%s'", gateway_id, vpc_id)
        collection.update_one(
            filter={"_id": gateway["_id"]},
            update={"$set": {"attachments": gateway["attachments"] + [{"vpc_id": vpc_id, "state": "available"}]}},
        )
