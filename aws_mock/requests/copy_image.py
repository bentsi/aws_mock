import logging

from aws_mock.lib import get_collection_by_resource_id, generate_resource_id, aws_response


LOGGER = logging.getLogger(__name__)


@aws_response
def copy_image(source_region_name: str, source_ami_id: str, target_region_name: str) -> dict:
    target_ami_id = generate_resource_id(resource_type="ami")

    LOGGER.debug("Copy image %s/%s to %s/%s", source_region_name, source_ami_id, target_region_name, target_ami_id)
    get_collection_by_resource_id(resource_id=target_ami_id).insert_one({
        "id": target_ami_id,
        "region_name": target_region_name,
        "tags": {},
    })

    return {"image_id": target_ami_id}
