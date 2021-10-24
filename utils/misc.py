import random
import string
from typing import Dict

from schema.tags import AWSTag


def random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def random_int(length: int) -> int:
    return int(''.join(random.choices(string.digits, k=length)))


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


def aws_tags_from_dict(tags: Dict[str, str]):
    return [AWSTag(key=tag_name, value=str(tag_value)) for tag_name, tag_value in tags.items()]
