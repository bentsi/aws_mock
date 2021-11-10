from flask import render_template

from aws_mock.lib import get_aws_mock_db


def describe_vpcs() -> str:
    vpc = get_aws_mock_db()["vpc"].find_one() or {}
    return render_template("responses/describe_vpc.xml", id=vpc.get("id"), tags=vpc.get("tags"))
