from flask import render_template

from aws_mock.lib import get_aws_mock_db


def describe_security_groups() -> str:
    items = []
    for security_group in get_aws_mock_db()["sg"].find():
        items.append(render_template(
            "responses/describe_security_groups_item.xml",
            security_group_id=security_group["id"],
            tags=security_group.get("tags"),
            is_ingress_rules_added=security_group.get("is_ingress_rules_added"),
        ))
    return render_template("responses/describe_security_groups.xml", items=items)
