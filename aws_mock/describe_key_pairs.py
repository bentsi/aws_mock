from flask import render_template

from aws_mock.lib import get_aws_mock_db


def describe_key_pairs(key_name: str) -> tuple[str, int] | str:
    if key_pair := get_aws_mock_db()["key"].find_one({"name": key_name}):
        return render_template(
            "responses/describe_key_pairs.xml",
            key_name=key_name,
            key_pair_id=key_pair["id"],
            tags=key_pair.get("tags"),
        )
    return render_template("responses/describe_key_pairs_not_found.xml", key_name=key_name), 400
