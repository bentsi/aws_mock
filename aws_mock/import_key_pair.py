import logging

from flask import render_template

from aws_mock.lib import get_collection_by_resource_id, generate_resource_id


LOGGER = logging.getLogger(__name__)


def import_key_pair(key_name: str) -> str:
    key_pair_id = generate_resource_id(resource_type="key")

    LOGGER.debug("Import key pair `%s', id=`%s'", key_name, key_pair_id)
    get_collection_by_resource_id(resource_id=key_pair_id).insert_one({"id": key_pair_id, "name": key_name})

    return render_template("responses/import_key_pair.xml", key_name=key_name, key_pair_id=key_pair_id)
