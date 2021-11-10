import logging

from flask import render_template
from aws_mock.lib import get_aws_mock_db, get_collection_name


LOGGER = logging.getLogger(__name__)


def create_tags(resource_ids: list[str], tags: dict[str, str]) -> str:
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
    return render_template("responses/create_tags.xml")
