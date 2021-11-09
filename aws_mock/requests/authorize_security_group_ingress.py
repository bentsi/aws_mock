import logging

from aws_mock.lib import get_collection_by_resource_id, aws_response


LOGGER = logging.getLogger(__name__)


@aws_response
def authorize_security_group_ingress(security_group_id: str) -> dict:
    collection = get_collection_by_resource_id(resource_id=security_group_id)
    if security_group := collection.find_one({"id": security_group_id}):
        LOGGER.debug("Add ingress rules for `%s'", security_group_id)
        collection.update_one(
            filter={"_id": security_group["_id"]},
            update={"$set": {"is_ingress_rules_added": True}},
        )
    return {"security_group_id": security_group_id}
