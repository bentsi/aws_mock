from flask import render_template

from aws_mock.lib import get_region_name_from_hostname, get_short_region_name


def describe_availability_zones(hostname: str) -> str:
    region_name = get_region_name_from_hostname(hostname=hostname)
    return render_template(
        "responses/describe_availability_zones.xml",
        region_name=region_name,
        short_region_name=get_short_region_name(region_name),
    )
