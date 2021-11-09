from aws_mock.lib import get_aws_mock_db, aws_response


@aws_response
def describe_subnets(subnet_name: str) -> dict:
    return {"items": list(get_aws_mock_db()["subnet"].find({"tags.Name": subnet_name}))}
