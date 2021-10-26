from flask import render_template

from aws_mock.lib import get_aws_mock_db


def describe_subnets(subnet_name: str) -> str:
    items = []
    for subnet in get_aws_mock_db()["subnet"].find({"tags.Name": subnet_name}):
        items.append(render_template("responses/subnet_item.xml", **subnet))
    return render_template("responses/describe_subnets.xml", items=items)
