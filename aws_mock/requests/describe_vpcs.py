from aws_mock.lib import get_aws_mock_db, aws_response


@aws_response
def describe_vpcs() -> dict:
    return {"items": list(get_aws_mock_db()["vpc"].find())}
