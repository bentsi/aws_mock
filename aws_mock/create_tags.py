import logging
from uuid import uuid4

from flask import Flask, request, render_template
from aws_mock.lib import extract_tags, get_collection_name, get_aws_mock_db

LOGGER = logging.getLogger(__name__)


app = Flask(__name__)


def do_create_tags(resource_ids: list[str], tags: dict[str, str]) -> str:
    LOGGER.debug("Update resource_ids=%r with tags=%r", resource_ids, tags)
    db = get_aws_mock_db()
    for resource_id in resource_ids:
        collection = db[get_collection_name(resource_id)]
        if resource := collection.find_one({"id": resource_id}):
            LOGGER.debug("Update tags for %s", resource_id)
            collection.update_one(
                filter={"_id": resource["_id"]},
                update={"$set": {
                    "tags": resource.get("tags", {}) | tags,
                }},
            )
    return render_template("responses/create_tags.xml", request_id=str(uuid4()))


@app.route("/", methods=["POST"])
def index():
    match request.form["Action"]:
        case "CreateTags":
            resource_ids = [value for key, value in request.form.items() if key.startswith("ResourceId.")]
            tags = extract_tags(request.form)
            return do_create_tags(resource_ids=resource_ids, tags=tags)
