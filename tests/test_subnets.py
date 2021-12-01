from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.conftest import REGION_NAME

if TYPE_CHECKING:
    from unittest.mock import Mock

    from mypy_boto3_ec2 import EC2Client, EC2ServiceResource

    from tests.conftest import RunQueryFunc


SUBNET_NAME = "my-subnet"


def test_create_subnet(run_query: RunQueryFunc, mongo: Mock) -> None:
    response = run_query({
        "Action": "CreateSubnet",
        "Version": "2016-11-15",
        "CidrBlock": "10.0.0.0/22",
        "Ipv6CidrBlock": "",
        "VpcId": "vpc-0b04728271b54803d",
        "AvailabilityZone": f"{REGION_NAME}a",
    })
    assert b"CreateSubnetResponse" in response.data
    assert b"<state>available</state>" in response.data
    mongo().aws_mock["subnet"].insert_one.assert_called_once()


def test_describe_subnets_filtered_by_name_empty_list(run_query: RunQueryFunc, mongo: Mock) -> None:
    response = run_query({
        "Action": "DescribeSubnets",
        "Filter.1.Name": "tag:Name",
        "Filter.1.Value.1": f"SCT-subnet-{REGION_NAME}a",
    })
    assert b"DescribeSubnetsResponse" in response.data
    mongo().aws_mock["subnet"].find.assert_called_once()


def test_describe_subnets_filtered_by_name(run_query: RunQueryFunc, mongo: Mock) -> None:
    mongo().aws_mock["subnet"].find.return_value = [{
        "id": "subnet-12345",
        "region_name": "eu-north-1",
        "vpc_id": "vpc-12345",
        "cidr_block": "10.0.0.0/16",
        "ipv6_cidr_block": "2406:da16:5be:8800::/64",
        "availability_zone": "eu-north-1a",
        "availability_zone_id": "eun-az1",
        "tags": {"Name": "subnet1", "Owner": "qa"},
    }]
    response = run_query({
        "Action": "DescribeSubnets",
        "Filter.1.Name": "tag:Name",
        "Filter.1.Value.1": f"SCT-subnet-{REGION_NAME}a",
    })
    assert b"DescribeSubnetsResponse" in response.data
    mongo().aws_mock["subnet"].find.assert_called_once()


def test_modify_subnet_attribute(run_query: RunQueryFunc, mongo: Mock) -> None:
    response = run_query({
        "Action": "ModifySubnetAttribute",
        "Version": "2016-11-15",
        "MapPublicIpOnLaunch.Value": "true",
        "SubnetId": "subnet-0bec8219a55cf9bb4",
    })
    assert b"ModifySubnetAttributeResponse" in response.data
    assert b"<return>true</return>" in response.data
    mongo().aws_mock["subnet"].find.assert_not_called()


@pytest.mark.integration
def test_create_subnet_boto3(ec2_client: EC2Client) -> None:
    result = ec2_client.create_subnet(
        CidrBlock="10.0.0.0/24",
        Ipv6CidrBlock="2406:da16:5be:8800::/64",
        AvailabilityZone=f"{REGION_NAME}a",
        VpcId="vpc-0000000001",
    )
    assert result


@pytest.mark.integration
def test_describe_subnets_boto3(ec2_client: EC2Client, ec2_resource: EC2ServiceResource) -> None:
    result = ec2_client.describe_subnets(Filters=[{"Name": "tag:Name", "Values": [SUBNET_NAME]}])
    assert not result["Subnets"]

    result = ec2_client.create_subnet(
        CidrBlock="10.0.0.0/24",
        Ipv6CidrBlock="2406:da16:5be:8800::/64",
        AvailabilityZone=f"{REGION_NAME}a",
        VpcId="vpc-0000000001",
    )
    subnet = ec2_resource.Subnet(result["Subnet"]["SubnetId"])
    subnet.create_tags(Tags=[{"Key": "Name", "Value": SUBNET_NAME}])
    result = ec2_client.describe_subnets(Filters=[{"Name": "tag:Name", "Values": [SUBNET_NAME]}])
    assert result["Subnets"]


@pytest.mark.integration
def test_modify_subnet_attribute_with_boto3(ec2_client: EC2Client) -> None:
    response = ec2_client.modify_subnet_attribute(
        MapPublicIpOnLaunch={"Value": True},
        SubnetId="subnet-0000000001",
    )
    assert response["ResponseMetadata"]
