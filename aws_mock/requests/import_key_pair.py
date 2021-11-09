import logging

from aws_mock.lib import get_collection_by_resource_id, generate_resource_id, aws_response


LOGGER = logging.getLogger(__name__)


@aws_response
def import_key_pair(key_name: str) -> dict:
    key_pair_id = generate_resource_id(resource_type="key")
    key_pair = {"id": key_pair_id, "name": key_name, "tags": {}}

    LOGGER.debug("Import key pair `%s', id=`%s'", key_name, key_pair_id)
    get_collection_by_resource_id(resource_id=key_pair_id).insert_one(key_pair)

    return {"item": key_pair}
