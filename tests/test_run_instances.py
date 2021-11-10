from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from tests.base import AwsMockTestCase


class TestRunInstances(AwsMockTestCase):
    def setUp(self):
        super().setUp()
        self.request_body = {
            "Action": "RunInstances",
            "Version": "2016-11-15",
            "ImageId": "ami-008c29ad053756fc9",
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
        }

    @patch("aws_mock.lib.MongoClient")
    def test_all(self, mongo: Mock):
        response = self.app.post(self.base_url, data=self.request_body)
        response_text = response.data.decode()
        soup = BeautifulSoup(response_text, "xml")
        mongo().aws_mock["i"].insert_one.assert_called_once()
        self.assertEqual(soup.instancesSet.item.imageId.text, self.request_body["ImageId"])

    def test_with_boto3(self):  # pylint: disable=no-self-use
        expected_image_id = "ami-008c29ad053756fc9"
        result = self.ec2_resource.create_instances(ImageId=expected_image_id, MinCount=1, MaxCount=1)
        assert len(result) == 1
        instance = result[0]
        assert instance.image_id == expected_image_id
