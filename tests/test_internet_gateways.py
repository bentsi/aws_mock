from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.conftest import REGION_NAME

if TYPE_CHECKING:
    from unittest.mock import Mock

    from mypy_boto3_ec2 import EC2Client, EC2ServiceResource

    from tests.conftest import RunQueryFunc


INTERNET_GATEWAY_NAME = "my-gateway"


def test_create_internet_gateway(run_query: RunQueryFunc, mongo: Mock) -> None:
    response = run_query({
        "Action": "CreateInternetGateway",
        "Version": "2016-11-15",
    })
    assert b"CreateInternetGatewayResponse" in response.data
    assert b"<attachmentSet/>" in response.data
    mongo().aws_mock["igw"].insert_one.assert_called_once()


def test_describe_internet_gateways_filtered_by_name(run_query: RunQueryFunc, mongo: Mock) -> None:
    response = run_query({
        "Action": "DescribeInternetGateways",
        "Version": "2016-11-15",
        "Filter.1.Name": "tag:Name",
        "Filter.1.Value.1": f"SCT-igw-{REGION_NAME}a",
    })
    assert b"DescribeInternetGateways" in response.data
    mongo().aws_mock["igw"].find.assert_called_once()


@pytest.mark.integration
def test_create_and_describe_gateways_boto3(ec2_client: EC2Client, ec2_resource: EC2ServiceResource) -> None:
    result = ec2_client.describe_internet_gateways(Filters=[{"Name": "tag:Name", "Values": [INTERNET_GATEWAY_NAME]}])
    assert not result["InternetGateways"]

    igw = ec2_resource.InternetGateway(ec2_client.create_internet_gateway()["InternetGateway"]["InternetGatewayId"])
    igw.create_tags(Tags=[{"Key": "Name", "Value": INTERNET_GATEWAY_NAME}])
    result = ec2_client.describe_internet_gateways(Filters=[{"Name": "tag:Name", "Values": [INTERNET_GATEWAY_NAME]}])
    assert result["InternetGateways"]

    result = igw.attach_to_vpc(VpcId="vpc-00000000001")
    assert result["ResponseMetadata"]
