from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from aws_mock.predefined import ROUTE_TABLE

if TYPE_CHECKING:
    from unittest.mock import Mock

    from mypy_boto3_ec2 import EC2Client

    from tests.conftest import RunQueryFunc


ROUTE_TABLE_NAME = "my-subnet"


def test_describe_route_tables_filtered_by_name(run_query: RunQueryFunc, mongo: Mock) -> None:
    response = run_query({
        "Action": "DescribeRouteTables",
        "Version": "2016-11-15",
        "Filter.1.Name": "tag:Name",
        "Filter.1.Value.1": "SCT-rt",
    })
    assert b"DescribeRouteTablesResponse" in response.data
    mongo().aws_mock["rtb"].find.assert_not_called()


def test_describe_route_tables_filtered_by_vpc_id(run_query: RunQueryFunc, mongo: Mock) -> None:
    response = run_query({
        "Action": "DescribeRouteTables",
        "Version": "2016-11-15",
        "Filter.1.Name": "vpc-id",
        "Filter.1.Value.1": ROUTE_TABLE["vpc_id"],
    })
    assert b"DescribeRouteTablesResponse" in response.data
    mongo().aws_mock["rtb"].find.assert_not_called()


@pytest.mark.integration
def test_describe_route_tables_filtered_by_name_boto3(ec2_client: EC2Client) -> None:
    result = ec2_client.describe_route_tables(Filters=[{
        "Name": "tag:Name",
        "Values": [ROUTE_TABLE_NAME],
    }])
    assert result["RouteTables"]


@pytest.mark.integration
def test_describe_route_tables_filtered_by_vpc_id_boto3(ec2_client: EC2Client) -> None:
    result = ec2_client.describe_route_tables(Filters=[{
        "Name": "vpc-id",
        "Values": [ROUTE_TABLE["vpc_id"]],
    }])
    assert result["RouteTables"]
