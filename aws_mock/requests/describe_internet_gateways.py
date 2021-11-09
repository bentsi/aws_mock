from aws_mock.lib import get_aws_mock_db, aws_response


@aws_response
def describe_internet_gateways(gateway_name: str) -> dict:
    return {"items": list(get_aws_mock_db()["igw"].find({'tags.Name': gateway_name}))}
