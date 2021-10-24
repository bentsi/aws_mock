from __future__ import annotations
from typing import TYPE_CHECKING
from pymongo import MongoClient

if TYPE_CHECKING:
    from werkzeug.datastructures import ImmutableMultiDict


def extract_tags(form: ImmutableMultiDict[str, str]) -> dict[str, str]:
    tags = {}
    for i in range(1, 51):  # each resource can have a maximum of 50 tags
        if key := form.get(f"Tag.{i}.Key"):
            tags[key] = form[f"Tag.{i}.Value"]
            continue
        return tags


def get_collection_name(resource_id):
    return resource_id.split("-", maxsplit=1)[0]


def get_aws_mock_db():
    return MongoClient().aws_mock