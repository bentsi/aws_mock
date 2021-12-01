from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unittest.mock import Mock

    from tests.conftest import RunQueryFunc


VPC_ID = "vpc-12345"


def test_create_vpc(run_query: RunQueryFunc, mongo: Mock) -> None:
    mongo().aws_mock["vpc"].find.return_value = [{"_id": "MOCKED_ID", "id": VPC_ID}]
    response = run_query({
        "Action": "CreateVpc",
        "Version": "2016-11-15",
        "CidrBlock": "10.0.0.0/16",
        "AmazonProvidedIpv6CidrBlock": True,
    })
    assert b"vpcId" in response.data
    assert b"<cidrBlock>10.0.0.0/16</cidrBlock>" in response.data


def test_describe_vpcs(run_query: RunQueryFunc, mongo: Mock) -> None:
    mongo().aws_mock["vpc"].find.return_value = [{
        "_id": "MOCKED_ID",
        "id": VPC_ID,
        "tags": {},
    }]
    response = run_query({
        "Action": "DescribeVpcs",
        "Version": "2016-11-15",
        "VpcId": VPC_ID,
        "CidrBlock": "10.0.0.0/16",
        "AmazonProvidedIpv6CidrBlock": True,
    })
    assert b"cidrBlock" in response.data
    assert f"<vpcId>{VPC_ID}</vpcId>".encode("ascii") in response.data
