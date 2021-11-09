from aws_mock.lib import get_aws_mock_db, aws_response
from aws_mock.predefined import MASTER_REGION_NAME, MASTER_REGION_IMAGE


@aws_response
def describe_images(region_name: str) -> dict:
    if region_name == MASTER_REGION_NAME:
        return {"items": [MASTER_REGION_IMAGE]}
    return {"items": list(get_aws_mock_db()["ami"].find({"region_name": region_name}))}
