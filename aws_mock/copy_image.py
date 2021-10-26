import logging

from flask import render_template
from aws_mock.lib import get_collection_by_resource_id, generate_resource_id


LOGGER = logging.getLogger(__name__)


def copy_image(source_region: str, source_ami_id: str, target_region: str) -> str:
    target_ami_id = generate_resource_id(resource_type="ami")

    LOGGER.debug("Copy image from %s/%s to %s/%s", source_region, source_ami_id, target_region, target_ami_id)
    get_collection_by_resource_id(resource_id=target_ami_id).insert_one({"id": target_ami_id, "region": target_region})

    return render_template("responses/copy_image.xml", image_id=target_ami_id)
