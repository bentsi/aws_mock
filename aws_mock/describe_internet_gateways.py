from flask import render_template

from aws_mock.lib import get_aws_mock_db


def describe_internet_gateways(gateway_name: str) -> str:
    items = []
    for gateway in get_aws_mock_db()["igw"].find({'tags.Name': gateway_name}):
        items.append(render_template("responses/internet_gateway_item.xml", **gateway))
    return render_template("responses/describe_internet_gateways.xml", items=items)
