from __future__ import annotations

import os
import socket
from functools import wraps
from random import getrandbits
from typing import TYPE_CHECKING, ParamSpec

from flask import render_template
from pymongo import MongoClient
from werkzeug.debug import DebuggedApplication

if TYPE_CHECKING:
    from typing import Callable, TypeAlias

    from flask import Flask
    from pymongo.database import Database
    from pymongo.collection import Collection
    from werkzeug.datastructures import ImmutableMultiDict


def extract_tags(form: ImmutableMultiDict[str, str], prefix: str = "") -> dict[str, str]:
    tags = {}
    for i in range(1, 51):  # each resource can have a maximum of 50 tags
        if key := form.get(f"{prefix}Tag.{i}.Key"):
            tags[key] = form[f"{prefix}Tag.{i}.Value"]
            continue
        return tags


def get_aws_mock_db() -> Database:
    return MongoClient().aws_mock


def get_collection_name(resource_id: str) -> str:
    return resource_id.split("-", maxsplit=1)[0]


def get_collection_by_resource_id(resource_id: str) -> Collection:
    return get_aws_mock_db()[get_collection_name(resource_id=resource_id)]


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


P = ParamSpec("P")
AwsResponseArgs: TypeAlias = dict | tuple[dict, int] | tuple[str, dict, int] | tuple[str, int] | None


def aws_response(func: Callable[P, AwsResponseArgs]) -> Callable[P, tuple[str, int]]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[str, int]:
        template, ctx, status_code = f"responses/{func.__name__}.xml", {}, 200
        match func(*args, **kwargs):
            case None:
                pass
            case str(response), int(status_code):
                return response, status_code
            case str(template), dict(ctx), int(status_code):
                pass
            case dict(ctx), int(status_code):
                pass
            case dict(ctx):
                pass
            case result:
                raise ValueError(f"Wrapped function returned unexpected values: {result:r}")
        return render_template(template, **ctx), status_code
    return wrapper


# Module distutils is deprecated and PEP-632 suggested to reimplement this function.
def strtobool(val: str) -> bool:
    """Convert a string representation of truth to True or False.

    True values are 'y', 'yes', 't', 'true', 'on', and '1'.
    False values are 'n', 'no', 'f', 'false', 'off', '0' and ''.
    Raises ValueError if 'val' is anything else.
    """
    match val.lower():
        case "y" | "yes" | "t" | "true" | "on" | "1":
            return True
        case "n" | "no" | "f" | "false" | "off" | "0" | "":
            return False
    raise ValueError(f"invalid truth value {val!r}")


def set_debug(app: Flask) -> Flask:
    if strtobool(os.environ.get("AWS_MOCK_DEVMODE", "false")):
        app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
        app.debug = True
    return app
