import logging

from flask import render_template
from werkzeug.datastructures import ImmutableMultiDict
from aws_mock.lib import get_collection_name, get_aws_mock_db, extract_tags, generate_resource_id


LOGGER = logging.getLogger(__name__)


def run_instances(request_data: ImmutableMultiDict[str, str]) -> str:
    """
        Doc: https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_RunInstances.html
    """
    num_instances = int(request_data["MaxCount"])
    db = get_aws_mock_db()

    LOGGER.debug(f"Creating %s instances...", num_instances)
    items = []
    for _ in range(num_instances):
        instance_id = generate_resource_id(resource_type="i")
        db[get_collection_name(instance_id)].insert_one({"id": instance_id, "tags": extract_tags(request_data)})
        items.append(render_template("responses/run_instances_item.xml", instance_id=instance_id))

    return render_template("responses/run_instances.xml", items=items)
