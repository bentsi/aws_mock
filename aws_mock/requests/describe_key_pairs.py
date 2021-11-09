from aws_mock.lib import get_aws_mock_db, aws_response


@aws_response
def describe_key_pairs(key_name: str) -> dict | tuple[str, dict, int]:
    if key_pair := get_aws_mock_db()["key"].find_one({"name": key_name}):
        return {"items": [key_pair]}
    return "responses/describe_key_pairs_not_found.xml", {"key_name": key_name}, 400
