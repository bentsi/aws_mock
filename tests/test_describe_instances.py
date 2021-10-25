import unittest
import boto3
from bs4 import BeautifulSoup
from unittest.mock import Mock, patch
from aws_mock.describe_instances import app


class TestRunInstances(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        self.app = app.test_client()
        self.base_url = '/'
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
        ec2 = boto3.resource("ec2", region_name="eu-north-1")
        expected_image_id = 'ami-008c29ad053756fc9'
        result = ec2.create_instances(ImageId=expected_image_id, MinCount=1, MaxCount=1)
        assert len(result) == 1
        instance = result[0]
        ec2 = boto3.client("ec2", region_name="eu-north-1")
        instances = ec2.describe_instances(InstanceIds=[instance.id])
        assert instances['Reservations'][0]['Instances'][0]['InstanceId'] == instance.id
