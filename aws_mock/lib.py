from __future__ import annotations
from typing import TYPE_CHECKING, Optional
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


def get_region_name_from_hostname(hostname: str, default='eu-central-1') -> str:
    # url_data.hostname = ec2.ap-northeast-3.amazonaws.com
    url_chunks = hostname.split('.', maxsplit=3)
    if len(url_chunks) != 3 or len(url_chunks[1].split('-')) != 3:
        return default
    return url_chunks[1]


def get_short_region_name(region_name: str) -> Optional[str]:
    # ap-northeast-3 -> apne3
    chunks = region_name.split('-')
    if len(chunks) != 3:
        return None
    output = chunks[0]
    chunk = chunks[1]
    while chunk:
        for prefix in ['north', 'south', 'east', 'west', 'central']:
            if chunk.startswith(prefix):
                output += prefix[0]
                chunk = chunk[len(prefix):]
                break
        else:
            return None
    chunk = chunks[2]
    if not chunk.isdigit():
        return None
    return output + chunk


