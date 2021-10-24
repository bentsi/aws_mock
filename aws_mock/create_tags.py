from __future__ import annotations

import logging
from uuid import uuid4
from typing import TYPE_CHECKING

from flask import Flask, request, render_template
from pymongo import MongoClient

if TYPE_CHECKING:
    from werkzeug.datastructures import ImmutableMultiDict


LOGGER = logging.getLogger(__name__)


app = Flask(__name__)


def extract_tags(form: ImmutableMultiDict[str, str]) -> dict[str, str]:
    tags = {}
    for i in range(1, 51):  # each resource can have a maximum of 50 tags
        if key := form.get(f"Tag.{i}.Key"):
            tags[key] = form[f"Tag.{i}.Value"]
            continue
        return tags


def do_create_tags(resource_ids: list[str], tags: dict[str, str]) -> str:
    LOGGER.debug("Update resource_ids=%r with tags=%r", resource_ids, tags)
    db = MongoClient().aws_mock
    for resource_id in resource_ids:
        collection = db[resource_id.split("-", maxsplit=1)[0]]
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
