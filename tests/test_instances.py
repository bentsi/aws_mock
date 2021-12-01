from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from bs4 import BeautifulSoup

from aws_mock.predefined import MASTER_REGION_IMAGE
from tests.conftest import REGION_NAME

if TYPE_CHECKING:
    from unittest.mock import Mock

    from mypy_boto3_ec2 import EC2Client, EC2ServiceResource

    from tests.conftest import RunQueryFunc


IMAGE_ID = MASTER_REGION_IMAGE["id"]
INSTANCE_ID = "i-12345"


def test_run_instances(run_query: RunQueryFunc, mongo: Mock) -> None:
    response = run_query({
        "Action": "RunInstances",
        "Version": "2016-11-15",
        "ImageId": IMAGE_ID,
        "InstanceType": "i3.large",
        "MinCount": 1,
        "MaxCount": 1,
        "KeyName": "scylla-qa-ec2",
        "NetworkInterface.1.DeviceIndex": 0,
        "NetworkInterface.1.AssociatePublicIpAddress": "true",
        "NetworkInterface.1.SubnetId": "subnet-0a6f57a00ff595d6a",
        "NetworkInterface.1.SecurityGroupId.1": "sg-0b679cc07b33bc636",
        "NetworkInterface.1.DeleteOnTermination": "true",
        "TagSpecification.1.ResourceType": "instance",
        "TagSpecification.1.Tag.1.Key": "TestId",
        "TagSpecification.1.Tag.1.Value": "37114f4d-8108-4c16-ba95-a19a2fee9249",
        "TagSpecification.1.Tag.2.Key": "NodeType",
        "TagSpecification.1.Tag.2.Value": "sct-runner",
        "TagSpecification.1.Tag.3.Key": "RunByUser",
        "TagSpecification.1.Tag.3.Value": "linux_user@dkropachev",
        "TagSpecification.1.Tag.4.Key": "keep",
        "TagSpecification.1.Tag.4.Value": "7",
        "TagSpecification.1.Tag.5.Key": "keep_action",
        "TagSpecification.1.Tag.5.Value": "terminate",
        "TagSpecification.1.Tag.6.Key": "Name",
        "TagSpecification.1.Tag.6.Value": "sct-runner-1.5-instance-37114f4d",
        "BlockDeviceMapping.1.DeviceName": "/dev/sda1",
        "BlockDeviceMapping.1.Ebs.VolumeSize": "80",
        "BlockDeviceMapping.1.Ebs.VolumeType": "gp2",
        "ClientToken": "b024bd1f-f215-4b4c-8043-59d59104cb35",
    })
    doc = BeautifulSoup(response.data.decode(), "xml")
    assert doc.instancesSet.item.imageId.text == IMAGE_ID
    mongo().aws_mock["i"].insert_many.assert_called_once()


def test_describe_instances(run_query: RunQueryFunc, mongo: Mock) -> None:
    mongo().aws_mock["i"].find.return_value = [{
        "_id": "MOCKED_ID",
        "id": INSTANCE_ID,
        "tags": {},
    }]
    response = run_query({
        "Action": "DescribeInstances",
        "Version": "2016-11-15",
        "InstanceId.1": INSTANCE_ID,
    })
    mongo().aws_mock["i"].find.assert_called_once()
    assert INSTANCE_ID in response.data.decode()


@pytest.mark.integration
def test_run_and_describe_instances_boto3(ec2_client: EC2Client, ec2_resource: EC2ServiceResource) -> None:
    subnet_id = ec2_client.create_subnet(
        CidrBlock="10.0.0.0/24",
        Ipv6CidrBlock="2406:da16:5be:8800::/64",
        AvailabilityZone=f"{REGION_NAME}a",
        VpcId="vpc-0000000001",
    )["Subnet"]["SubnetId"]
    security_group_id = ec2_client.create_security_group(
        Description="Created by test_run_intances_boto3",
        GroupName="my-group",
        VpcId="vpc-0000000001",
    )["GroupId"]
    result = ec2_resource.create_instances(
        ImageId=IMAGE_ID,
        MinCount=1,
        MaxCount=1,
        KeyName="scylla-qa-ec2",
        NetworkInterfaces=[{"SubnetId": subnet_id, "Groups": [security_group_id]}],
    )
    assert len(result) == 1

    instance = result[0]
    assert instance.image_id == IMAGE_ID

    instances = ec2_client.describe_instances(InstanceIds=[instance.id])
    assert instances["Reservations"][0]["Instances"][0]["InstanceId"] == instance.id
