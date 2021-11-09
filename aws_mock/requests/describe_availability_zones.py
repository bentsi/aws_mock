from aws_mock.lib import get_short_region_name, aws_response


@aws_response
def describe_availability_zones(region_name: str) -> dict:
    return {"region_name": region_name, "short_region_name": get_short_region_name(region_name)}
