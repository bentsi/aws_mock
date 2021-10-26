from __future__ import annotations

import socket
from random import getrandbits
from typing import TYPE_CHECKING

from pymongo import MongoClient

if TYPE_CHECKING:
    from pymongo.database import Database
    from pymongo.collection import Collection
    from werkzeug.datastructures import ImmutableMultiDict


def extract_tags(form: ImmutableMultiDict[str, str]) -> dict[str, str]:
    tags = {}
    for i in range(1, 51):  # each resource can have a maximum of 50 tags
        if key := form.get(f"Tag.{i}.Key"):
            tags[key] = form[f"Tag.{i}.Value"]
            continue
        return tags


def get_aws_mock_db() -> Database:
    return MongoClient().aws_mock


def get_collection_name(resource_id: str) -> str:
    return resource_id.split("-", maxsplit=1)[0]


def get_collection_by_resource_id(resource_id: str) -> Collection:
    return get_aws_mock_db()[get_collection_name(resource_id=resource_id)]


def aws_extract_request_data(request_data: dict) -> dict:
    data = {}
    for item, value in request_data.items():
        parent = data
        chunks = item.split('.')
        last_chunk = chunks.pop()
        for chunk in chunks:
            if chunk.isdigit():
                chunk = int(chunk) - 1
                if len(parent) > chunk:
                    current = parent[chunk]
                else:
                    current = {}
                    parent.append(current)
            else:
                if chunk in parent:
                    current = parent[chunk]
                else:
                    current = []
                    parent[chunk] = current
            parent = current
        if isinstance(parent, list):
            parent.append(value)
        elif isinstance(parent, dict):
            parent[last_chunk] = value
    return data


def get_region_name_from_hostname(hostname: str, default: str = 'eu-central-1') -> str:
    # ec2.ap-northeast-3.amazonaws.com -> ap-northeast-3
    url_chunks = hostname.split('.', maxsplit=3)
    if len(url_chunks) != 4 or len(url_chunks[1].split('-')) != 3:
        return default
    return url_chunks[1]


def get_short_region_name(region_name: str) -> str | None:
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


def get_availability_zone_id(availability_zone: str) -> str:
    # ap-northeast-3a -> apne3-az3
    az_prefix = get_short_region_name(region_name=availability_zone[:-1])
    return f"{az_prefix}-az{ord(availability_zone[-1]) - ord('a') + 1}"


def get_aws_mock_server_ip() -> str:
    return socket.gethostbyname(socket.gethostname())


def generate_resource_id(resource_type: str, length: int = 17) -> str:
    return f"{resource_type}-{getrandbits(length << 2):x}"
