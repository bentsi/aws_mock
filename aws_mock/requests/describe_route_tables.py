from aws_mock.lib import aws_response
from aws_mock.predefined import ROUTE_TABLE


@aws_response
def describe_route_tables() -> dict:
    return {"items": [ROUTE_TABLE]}
