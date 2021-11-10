from unittest.mock import Mock, patch

from tests.base import AwsMockTestCase


class TestDescribeInstances(AwsMockTestCase):
    def setUp(self):
        super().setUp()
        self.request_body = {
            "Action": "DescribeInstances",
            "Version": "2016-11-15",
            "InstanceId.1": "i-08cafe5e67f1a0bd2",
        }

    @patch("aws_mock.lib.MongoClient")
    def test_all(self, mongo: Mock):
        collection = mongo().aws_mock["i"]
        collection.find.return_value = [{"_id": "MOCKED_ID", "id": self.request_body["InstanceId.1"]}]
        response = self.app.post(self.base_url, data=self.request_body)
        response_text = response.data.decode()
        collection.find.assert_called_once()
        self.assertIn(self.request_body["InstanceId.1"], response_text)

    def test_with_boto3(self):
        instance = self.ec2_resource.create_instances(ImageId="ami-008c29ad053756fc9", MinCount=1, MaxCount=1)[0]
        instances = self.ec2_client.describe_instances(InstanceIds=[instance.id])
        assert instances['Reservations'][0]['Instances'][0]['InstanceId'] == instance.id
