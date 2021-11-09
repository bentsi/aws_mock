import logging

from aws_mock.lib import get_aws_mock_db, get_collection_name, aws_response


LOGGER = logging.getLogger(__name__)


@aws_response
def create_tags(resource_ids: list[str], tags: dict[str, str]) -> None:
    LOGGER.debug("Update resource_ids=%r with tags=%r", resource_ids, tags)
    aws_mock_db = get_aws_mock_db()
    for resource_id in resource_ids:
        collection = aws_mock_db[get_collection_name(resource_id=resource_id)]
        if resource := collection.find_one({"id": resource_id}):
            LOGGER.debug("Update tags for %s", resource_id)
            collection.update_one(
                filter={"_id": resource["_id"]},
                update={"$set": {
                    "tags": resource.get("tags", {}) | tags,
                }},
            )
